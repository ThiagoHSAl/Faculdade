"""
rag.py — Busca semântica sobre a base de conhecimento (Opção B do RAG).

Embeda o corpus de `base_conhecimento` com os embeddings do Gemini e recupera os trechos
mais próximos da consulta por similaridade de cosseno (numpy, sem FAISS/Chroma). O índice
é cacheado em disco (`kb_embeddings.npz`) e só é reconstruído quando o corpus muda (hash).
Mesma interface da busca por palavra-chave (`base_conhecimento.buscar`) → troca de backend
transparente, com fallback gracioso quando os embeddings estão indisponíveis (offline / sem
GEMINI_API_KEY).
"""
import os
import time
import hashlib
from pathlib import Path

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import base_conhecimento

_MODELO = "models/gemini-embedding-001"
_ARQ_CACHE = Path(__file__).resolve().parent / "kb_embeddings.npz"
# Progresso parcial do build incremental: embeddings já calculados, indexados pelo hash do
# texto de cada entrada. Sobrevive ao 429 da cota diária — o build retoma de onde parou.
_ARQ_PARCIAL = Path(__file__).resolve().parent / "kb_embeddings_parcial.npz"

_indice = None        # singleton: (matriz_normalizada, entradas, hash_corpus)
_cliente_emb = None   # cache do cliente de embeddings
_cache_query_emb: dict[str, list] = {}  # embedding por consulta (evita re-embeddar a mesma)


def _embed_query(texto: str) -> list:
    """Embedding de UMA consulta, cacheado por texto. Fiel à produção (task-type de query);
    reusar o mesmo vetor entre backends/execuções economiza cota sem alterar o resultado."""
    texto = texto or ""
    if texto not in _cache_query_emb:
        _cache_query_emb[texto] = _embeddings().embed_query(texto)
    return _cache_query_emb[texto]


def _embeddings() -> GoogleGenerativeAIEmbeddings:
    global _cliente_emb
    if _cliente_emb is None:
        chave = os.getenv("GEMINI_API_KEY")
        if not chave:
            raise RuntimeError("GEMINI_API_KEY ausente — sem embeddings.")
        _cliente_emb = GoogleGenerativeAIEmbeddings(model=_MODELO, google_api_key=chave)
    return _cliente_emb


def _hash_corpus(entradas: list[dict]) -> str:
    h = hashlib.sha256()
    for e in entradas:
        h.update(base_conhecimento.texto_indexavel(e).encode("utf-8"))
    return h.hexdigest()


def _normalizar(matriz: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(matriz, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return matriz / normas


# Lote/pausa respeitando o limite gratuito de embeddings do Gemini (100 req/min).
_LOTE = 80
_PAUSA_SEG = 62


def _embed_em_lotes(textos: list[str]) -> list:
    """Embeda em lotes com pausa entre eles (respeita a cota free) e backoff em 429."""
    emb = _embeddings()
    vetores: list = []
    for i in range(0, len(textos), _LOTE):
        lote = textos[i:i + _LOTE]
        for tentativa in range(6):
            try:
                vetores.extend(emb.embed_documents(lote))
                break
            except Exception as e:
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and tentativa < 5:
                    time.sleep(_PAUSA_SEG)
                else:
                    raise
        if i + _LOTE < len(textos):
            time.sleep(_PAUSA_SEG)  # respeita 100/min entre lotes
    return vetores


def _carregar_cache(h: str, entradas: list[dict]):
    """Carrega o índice do disco se o hash do corpus bater. Retorna a tupla ou None."""
    if not _ARQ_CACHE.exists():
        return None
    try:
        dados = np.load(_ARQ_CACHE, allow_pickle=True)
        if str(dados["hash"]) == h:
            return (_normalizar(dados["matriz"].astype("float32")), entradas, h)
    except Exception:
        pass
    return None


def _store_por_entrada() -> dict:
    """Reúne os embeddings disponíveis por entrada (índice oficial + build parcial) num mapa
    {hash_do_texto: vetor}. É a base do índice resiliente: cobre o que já foi embeddado,
    mesmo que o corpus tenha crescido/mudado desde então (ex.: novo patch do Data Dragon)."""
    store: dict = {}
    if _ARQ_CACHE.exists():
        try:
            d = np.load(_ARQ_CACHE, allow_pickle=True)
            if "hashes" in d.files:  # formato novo: guarda o hash de cada entrada
                for h, v in zip(d["hashes"], d["matriz"]):
                    store[str(h)] = np.asarray(v, dtype="float32")
        except Exception:
            pass
    store.update(_carregar_parcial())  # progresso de um build em andamento, se houver
    return store


def _indice_por_entrada(entradas: list[dict]):
    """Monta o índice em memória a partir dos embeddings por entrada disponíveis, alinhados
    ao corpus ATUAL pelo hash de cada texto. Cobre só o subconjunto já embeddado (degradação
    graciosa) — não exige que o corpus inteiro bata. Retorna (matriz, entradas_cobertas) ou
    None se não houver nenhuma cobertura."""
    store = _store_por_entrada()
    if not store:
        return None
    cobertas, vetores = [], []
    for e in entradas:
        v = store.get(_hash_entrada(base_conhecimento.texto_indexavel(e)))
        if v is not None:
            cobertas.append(e)
            vetores.append(v)
    if not cobertas:
        return None
    return _normalizar(np.array(vetores, dtype="float32")), cobertas


def construir_indice(forcar: bool = False, permitir_construir: bool = True):
    """Carrega o índice (memória → cache exato → cobertura parcial por entrada) e, se
    necessário e permitido, o (re)constrói embeddando o corpus em lotes. Com
    `permitir_construir=False`, NUNCA embeda: usa só o que já existe em disco — mesmo que
    cubra o corpus apenas parcialmente — é o modo de runtime. A construção pesada é offline
    (CLI: `python rag.py`)."""
    global _indice
    entradas = base_conhecimento.entradas()
    h = _hash_corpus(entradas)

    if _indice is not None and _indice[2] == h and not forcar:
        return _indice

    if not forcar:
        cache = _carregar_cache(h, entradas)  # caminho rápido: cache exato (cobertura total)
        if cache is not None:
            _indice = cache
            return _indice
        parcial = _indice_por_entrada(entradas)  # resiliente: cobre o subconjunto embeddado
        if parcial is not None:
            _indice = (parcial[0], parcial[1], h)
            return _indice

    if not permitir_construir:
        return None  # nada em disco e proibido embeddar → quem chama cai no keyword

    textos = [base_conhecimento.texto_indexavel(e) for e in entradas]
    hashes = [_hash_entrada(t) for t in textos]
    matriz = np.array(_embed_em_lotes(textos), dtype="float32")
    try:
        np.savez(_ARQ_CACHE, matriz=matriz, hash=np.array(h), hashes=np.array(hashes))
    except Exception:
        pass  # sem permissão de escrita → segue só em memória
    _indice = (_normalizar(matriz), entradas, h)
    return _indice


def carregar_indice():
    """Carrega o índice já construído (cache), sem nunca embeddar. None se não existir."""
    return construir_indice(permitir_construir=False)


def _scores_semanticos(consulta: str):
    """(scores_crus, scores_com_boost_curado, entradas) para a consulta. Levanta se não
    houver índice pré-construído (quem chama trata / cai no keyword)."""
    indice = construir_indice(permitir_construir=False)
    if indice is None:
        raise RuntimeError("Índice semântico não construído (rode: python rag.py).")
    matriz, entradas, _ = indice
    q = np.array(_embed_query(consulta or ""), dtype="float32")
    q = q / (np.linalg.norm(q) or 1.0)
    scores = matriz @ q
    # Ranqueia pelo cosseno CRU. NÃO reaplicamos o BOOST_CURADO aqui: o boost é um score
    # inteiro de sobreposição de termos do keyword; multiplicá-lo sobre a similaridade de
    # cosseno (faixa estreita ~0.6-0.85) reordena tudo e enterra entradas factuais de
    # entrada única (item/feitiço/runa) que são o match #1 cru. A prioridade do conteúdo
    # curado continua garantida pelo keyword dentro da fusão híbrida (RRF).
    return scores, scores, entradas


def buscar_semantico(consulta: str, k: int = 4, limiar: float = 0.5) -> list[dict]:
    """Retorna as k entradas semanticamente mais próximas da consulta (cosseno), acima do
    limiar. Usa só o índice pré-construído; se não houver, levanta erro (quem chama cai no
    keyword). Cada consulta gasta 1 embedding (leve)."""
    scores, ranqueado, entradas = _scores_semanticos(consulta)
    ordem = np.argsort(ranqueado)[::-1][:k]
    return [entradas[i] for i in ordem if scores[i] >= limiar]


def ranquear_semantico(consulta: str, limite: int = 20) -> list[dict]:
    """Ranking semântico (até `limite`), sem limiar rígido — a fusão híbrida decide. Levanta
    se não houver índice (quem chama trata / cai no keyword)."""
    _, ranqueado, entradas = _scores_semanticos(consulta)
    ordem = np.argsort(ranqueado)[::-1][:limite]
    return [entradas[i] for i in ordem]


def buscar_hibrido(consulta: str, k: int = 4, c: int = 60) -> list[dict]:
    """Busca híbrida por Reciprocal Rank Fusion (RRF): funde o ranking por palavra-chave com
    o semântico somando 1/(c + posição) de cada lista. Aproveita os dois sinais e é robusta a
    escalas diferentes. Se o índice semântico estiver indisponível, degrada para só-keyword."""
    kw = base_conhecimento.ranquear(consulta, limite=20)
    try:
        sem = ranquear_semantico(consulta, limite=20)
    except Exception:
        sem = []
    if not sem:
        return kw[:k]
    fundido: dict[str, float] = {}
    por_id: dict[str, dict] = {}
    for ranking in (kw, sem):
        for pos, e in enumerate(ranking):
            eid = e.get("id") or e.get("titulo")
            por_id[eid] = e
            fundido[eid] = fundido.get(eid, 0.0) + 1.0 / (c + pos)
    melhores = sorted(fundido, key=fundido.get, reverse=True)[:k]
    return [por_id[i] for i in melhores]


def recuperar(consulta: str, k: int = 4) -> list[dict]:
    """Recuperação com correção leve (CRAG-lite): tenta a busca híbrida; se vier vazia,
    reformula a consulta com sinônimos/jargão do domínio e tenta de novo; se ainda assim
    nada, devolve lista vazia (quem formata avisa "não encontrado, não invente"). Nunca
    levanta: em erro, cai na busca por palavra-chave."""
    try:
        itens = buscar_hibrido(consulta, k=k)
        if itens:
            return itens
        consulta2 = base_conhecimento.expandir_consulta(consulta)
        if consulta2 != (consulta or ""):
            itens = buscar_hibrido(consulta2, k=k)
            if itens:
                return itens
        return []
    except Exception:
        return base_conhecimento.buscar(consulta, k=k)


def _hash_entrada(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _carregar_parcial() -> dict:
    """Embeddings já calculados (hash_do_texto -> vetor). {} se não houver progresso."""
    if not _ARQ_PARCIAL.exists():
        return {}
    try:
        d = np.load(_ARQ_PARCIAL, allow_pickle=True)
        return {str(h): v for h, v in zip(d["hashes"], d["matriz"])}
    except Exception:
        return {}


def _salvar_parcial(store: dict) -> None:
    if not store:
        return
    np.savez(_ARQ_PARCIAL,
             hashes=np.array(list(store.keys())),
             matriz=np.array(list(store.values()), dtype="float32"))


def construir_indice_incremental() -> bool:
    """Build resumível: embeda o corpus em lotes salvando o progresso a cada lote. Se a cota
    diária estourar (429), salva o que tem e para — rode de novo (ex.: amanhã) que continua
    de onde parou. Ao completar TODAS as entradas, grava o índice oficial (`_ARQ_CACHE`) e
    apaga o parcial. Retorna True só quando o índice fica completo."""
    entradas = base_conhecimento.entradas()
    textos = [base_conhecimento.texto_indexavel(e) for e in entradas]
    hashes = [_hash_entrada(t) for t in textos]
    store = _carregar_parcial()
    # mantém só hashes ainda presentes no corpus (limpa entradas que sumiram)
    store = {h: v for h, v in store.items() if h in set(hashes)}
    faltando = [i for i, h in enumerate(hashes) if h not in store]
    print(f"{len(entradas)} entradas no corpus | {len(store)} já embeddadas | "
          f"faltam {len(faltando)}.")

    if faltando:
        emb = _embeddings()
        try:
            for j in range(0, len(faltando), _LOTE):
                idxs = faltando[j:j + _LOTE]
                vetores = emb.embed_documents([textos[i] for i in idxs])
                for i, v in zip(idxs, vetores):
                    store[hashes[i]] = np.asarray(v, dtype="float32")
                _salvar_parcial(store)  # progresso resiliente a 429
                print(f"  +{len(idxs)} (total {len(store)}/{len(entradas)})")
                if j + _LOTE < len(faltando):
                    time.sleep(_PAUSA_SEG)  # respeita o limite por minuto
        except Exception as e:
            _salvar_parcial(store)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"\nCota diária do Gemini atingida. Progresso salvo: "
                      f"{len(store)}/{len(entradas)}. Rode 'python rag.py' de novo "
                      f"(após o reset diário da cota) para continuar.")
                return False
            raise

    # todas as entradas embeddadas → monta a matriz na ordem do corpus e finaliza
    matriz = np.array([store[h] for h in hashes], dtype="float32")
    np.savez(_ARQ_CACHE, matriz=matriz, hash=np.array(_hash_corpus(entradas)),
             hashes=np.array(hashes))
    try:
        _ARQ_PARCIAL.unlink()
    except OSError:
        pass
    print(f"\nÍndice COMPLETO: {matriz.shape[0]} entradas x {matriz.shape[1]} dims "
          f"-> {_ARQ_CACHE.name}")
    return True


if __name__ == "__main__":
    print("Construindo índice semântico da base de conhecimento (build incremental, "
          "resumível — respeita a cota gratuita; pode exigir mais de um dia)...")
    construir_indice_incremental()
