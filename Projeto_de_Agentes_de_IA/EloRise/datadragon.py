"""
datadragon.py — Ingestor do Data Dragon (Riot) para a base de conhecimento.

Baixa os dados FACTUAIS de itens, runas, campeões e feitiços do CDN estático da Riot
(1 request por arquivo, por patch — sem chave de API, sem rate limit, ZERO consumo de
LLM) e gera entradas no mesmo schema de `base_conhecimento` (id/titulo/topico/tags/texto),
gravando em `conhecimento_datadragon.json`. O `base_conhecimento` carrega esse arquivo e a
busca (palavra-chave ou semântica) passa a cobrir esse conhecimento automaticamente.

Uso (rode uma vez por patch):
    venv/bin/python datadragon.py            # usa a versão mais recente e locale pt_BR
"""
import re
import json
import sys
from pathlib import Path

import requests

_BASE = "https://ddragon.leagueoflegends.com"
_ARQ_SAIDA = Path(__file__).resolve().parent / "conhecimento_datadragon.json"
_TIMEOUT = 15


def versao_mais_recente() -> str:
    return requests.get(f"{_BASE}/api/versions.json", timeout=_TIMEOUT).json()[0]


def _get(versao: str, locale: str, arquivo: str) -> dict:
    url = f"{_BASE}/cdn/{versao}/data/{locale}/{arquivo}"
    return requests.get(url, timeout=_TIMEOUT).json()


def _limpar_html(texto: str) -> str:
    """Remove tags HTML e placeholders de scaling do Data Dragon, deixando texto limpo."""
    if not texto:
        return ""
    t = re.sub(r"<br\s*/?>", " ", texto, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)        # demais tags
    t = re.sub(r"\{\{.*?\}\}", "", t)      # placeholders {{ e1 }}
    t = re.sub(r"@\w+@", "", t)            # variáveis @Ratio@
    t = t.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", t).strip()


def _encurtar(texto: str, limite: int = 700) -> str:
    return texto if len(texto) <= limite else texto[:limite].rsplit(" ", 1)[0] + "…"


# ──────────────────────────────────────────────
# Ingestores por recurso
# ──────────────────────────────────────────────
def ingerir_itens(versao: str, locale: str) -> list[dict]:
    dados = _get(versao, locale, "item.json")["data"]
    entradas = []
    for item_id, it in dados.items():
        gold = it.get("gold", {})
        # só itens compráveis na Fenda do Invocador (mapa 11) e com custo
        if not gold.get("purchasable") or not it.get("maps", {}).get("11"):
            continue
        if gold.get("total", 0) <= 0:
            continue
        nome = it.get("name", "").strip()
        if not nome:
            continue
        plain = it.get("plaintext", "")
        desc = _limpar_html(it.get("description", ""))
        texto = _encurtar(" ".join(p for p in [plain, desc] if p))
        entradas.append({
            "id": f"item_{item_id}",
            "titulo": f"Item: {nome}",
            "topico": f"item:{item_id}",
            "tags": ["item", "itemizacao", "build", nome, *it.get("tags", [])],
            "texto": f"{nome} (custo {gold.get('total')} de ouro). {texto}",
        })
    return entradas


def ingerir_runas(versao: str, locale: str) -> list[dict]:
    estilos = _get(versao, locale, "runesReforged.json")
    entradas = []
    for estilo in estilos:
        nome_estilo = estilo.get("name", "")
        for slot in estilo.get("slots", []):
            for runa in slot.get("runes", []):
                nome = runa.get("name", "")
                texto = _limpar_html(runa.get("longDesc") or runa.get("shortDesc", ""))
                entradas.append({
                    "id": f"runa_{runa.get('id')}",
                    "titulo": f"Runa: {nome} ({nome_estilo})",
                    "topico": f"runa:{runa.get('id')}",
                    "tags": ["runa", "runas", nome, nome_estilo],
                    "texto": f"{nome} — árvore {nome_estilo}. {_encurtar(texto)}",
                })
    return entradas


def ingerir_feiticos(versao: str, locale: str) -> list[dict]:
    dados = _get(versao, locale, "summoner.json")["data"]
    entradas = []
    for chave, sp in dados.items():
        if "CLASSIC" not in sp.get("modes", []):  # só feitiços da Fenda
            continue
        nome = sp.get("name", "")
        texto = _limpar_html(sp.get("description", ""))
        entradas.append({
            "id": f"feitico_{sp.get('key', chave)}",
            "titulo": f"Feitiço de invocador: {nome}",
            "topico": f"feitico:{sp.get('key', chave)}",
            "tags": ["feitico", "feiticos", "summoner spell", nome, chave],
            "texto": f"{nome}: {_encurtar(texto)}",
        })
    return entradas


# Rótulo de cada slot de habilidade: passiva + Q/W/E/R (na ordem do array `spells`).
_SLOTS_SKILL = ["Q", "W", "E", "R"]


def _entradas_habilidades(c: dict, nome: str, chave: str, tags_campeao: list) -> list[dict]:
    """Entradas (1 por habilidade) com a mecânica de cada skill: passiva + Q/W/E/R."""
    passiva = c.get("passive") or {}
    skills = [("Passiva", passiva)] + list(zip(_SLOTS_SKILL, c.get("spells", [])))
    entradas = []
    for slot, h in skills:
        nome_h = h.get("name", "")
        desc = _limpar_html(h.get("description", ""))
        if not nome_h or not desc:
            continue
        # Custo/recarga/alcance só existem nos spells (a passiva não tem).
        extras = []
        if h.get("cooldownBurn"):
            extras.append(f"recarga {h['cooldownBurn']}s")
        if h.get("costBurn") and h.get("costBurn") != "0":
            extras.append(f"custo {h['costBurn']} de {h.get('costType', 'recurso')}")
        if h.get("rangeBurn") and h.get("rangeBurn") != "self":
            extras.append(f"alcance {h['rangeBurn']}")
        sufixo = f" ({'; '.join(extras)})" if extras else ""
        entradas.append({
            "id": f"skill_{chave}_{slot}",
            "titulo": f"Habilidade de {nome} ({slot}): {nome_h}",
            "topico": f"habilidade:{chave}:{slot}",
            "tags": ["habilidade", "habilidades", "skill", "passiva" if slot == "Passiva"
                     else slot, nome, nome_h, *tags_campeao],
            "texto": _encurtar(f"{nome_h} — habilidade {slot} de {nome}{sufixo}. {desc}"),
        })
    return entradas


def ingerir_campeoes(versao: str, locale: str) -> list[dict]:
    dados = _get(versao, locale, "championFull.json")["data"]
    entradas = []
    for nome_id, c in dados.items():
        nome = c.get("name", "")
        titulo = c.get("title", "")
        tags = c.get("tags", [])
        chave = c.get("key", nome_id)
        blurb = _limpar_html(c.get("blurb", ""))
        dicas = " ".join(_limpar_html(d) for d in c.get("allytips", [])[:3])
        partes = [f"{nome}, {titulo}."]
        if tags:
            partes.append(f"Funções: {', '.join(tags)}.")
        if blurb:
            partes.append(blurb)
        if dicas:
            partes.append(f"Dicas: {dicas}")
        entradas.append({
            "id": f"campeao_{chave}",
            "titulo": f"Campeão: {nome} — {titulo}",
            "topico": f"campeao:{chave}",
            "tags": ["campeao", "campeoes", nome, nome_id, *tags],
            "texto": _encurtar(" ".join(partes), 800),
        })
        entradas += _entradas_habilidades(c, nome, chave, tags)
    return entradas


def coletar_entradas(versao: str = None, locale: str = "pt_BR") -> list[dict]:
    versao = versao or versao_mais_recente()
    entradas = []
    for nome, func in (("itens", ingerir_itens), ("runas", ingerir_runas),
                       ("feiticos", ingerir_feiticos), ("campeoes", ingerir_campeoes)):
        try:
            parte = func(versao, locale)
            print(f"  {nome}: {len(parte)} entradas")
            entradas += parte
        except Exception as e:
            print(f"  {nome}: FALHOU ({e})", file=sys.stderr)
    return entradas


def gerar_arquivo(versao: str = None, locale: str = "pt_BR") -> int:
    versao = versao or versao_mais_recente()
    print(f"Data Dragon {versao} ({locale}):")
    entradas = coletar_entradas(versao, locale)
    _ARQ_SAIDA.write_text(json.dumps(entradas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Total: {len(entradas)} entradas -> {_ARQ_SAIDA.name}")
    return len(entradas)


if __name__ == "__main__":
    gerar_arquivo()
