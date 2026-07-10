"""
insights_evolucao.py — Insights do tutor sobre a EVOLUÇÃO do jogador (aba Evolução).

Depois que o jogador inicia o treino (cria um plano), esta camada lê as partidas jogadas
DEPOIS do plano e gera uma análise em linguagem natural: o que melhorou, o que caiu e —
principalmente — POR QUÊ, cruzando cada métrica com o contexto real das partidas (campeão
jogado e suas características de classe, elo, desempenho do time, placar de abates e a
composição das equipes). O tom é sempre de APOIO MORAL com CRÍTICA CONSTRUTIVA.

É uma chamada única ao LLM (não o agente socrático): recebe um contexto factual já montado
a partir dos dados e devolve o texto pronto em Markdown. Os números vêm sempre do contexto
(anti-alucinação) — o modelo interpreta, não inventa estatísticas.
"""
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from config import METRIC_LABELS, ROLE_LABELS, nome_exibicao
from base_conhecimento import caracteristicas_campeao
from plano_treino import descrever_base_plano, progresso_metrica, meta_atingida

load_dotenv()

# Quantas partidas pós-plano detalhar no contexto (as mais recentes). Limita o tamanho do
# prompt sem perder a leitura da tendência recente.
_MAX_PARTIDAS_DETALHE = 8


def _nome_campeao(champion: str) -> str:
    """Nome de exibição do campeão (resolve o championName interno, ex.: MonkeyKing→Wukong)."""
    c = caracteristicas_campeao(champion)
    return c["nome"] if c else (champion or "?")


def _resumo_time(participantes: list, team_id_jogador: int) -> dict:
    """Separa a partida em aliados/inimigos (sem o próprio jogador entre os aliados) e
    calcula o placar de abates de cada equipe — sinal cru de 'o time foi bem/mal'."""
    aliados, inimigos = [], []
    abates_aliados = abates_inimigos = 0
    for p in participantes or []:
        nome = _nome_campeao(p.get("champion"))
        if p.get("team_id") == team_id_jogador:
            aliados.append(nome)
            abates_aliados += p.get("kills", 0)
        else:
            inimigos.append(nome)
            abates_inimigos += p.get("kills", 0)
    return {
        "aliados": aliados,
        "inimigos": inimigos,
        "abates_aliados": abates_aliados,
        "abates_inimigos": abates_inimigos,
    }


def coletar_partidas_pos_plano(dados_brutos: dict, posicao: str,
                               baseline_fim_ts: int = None) -> list[dict]:
    """Partidas jogadas na rota DEPOIS do plano (fim_ts > baseline_fim_ts), da mais recente
    para a mais antiga, cruzando `partidas_metricas` (métricas da rota) com `historico`
    (resultado, composição, placar). Cada item já traz o campeão, suas características de
    classe e o contexto do time."""
    posicao = (posicao or "").upper()
    historico = {h.get("match_id"): h for h in dados_brutos.get("historico", [])}
    partidas = []
    for pm in dados_brutos.get("partidas_metricas", []):
        if (pm.get("posicao") or "").upper() != posicao:
            continue
        h = historico.get(pm.get("match_id"))
        if not h:
            continue
        fim_ts = h.get("fim_ts", 0)
        if baseline_fim_ts and fim_ts <= baseline_fim_ts:
            continue
        jogador = h.get("jogador") or {}
        carac = caracteristicas_campeao(pm.get("champion")) or {}
        time = _resumo_time(h.get("participantes", []), jogador.get("team_id"))
        partidas.append({
            "fim_ts": fim_ts,
            "campeao": carac.get("nome") or _nome_campeao(pm.get("champion")),
            "classes": carac.get("classes", []),
            "funcoes_desc": carac.get("funcoes_desc", ""),
            "venceu": h.get("venceu", False),
            "kda": jogador.get("kda"),
            "kills": jogador.get("kills"), "deaths": jogador.get("deaths"),
            "assists": jogador.get("assists"),
            "kp": jogador.get("kp"),
            "cs_min": jogador.get("cs_min"),
            "metricas": pm.get("metricas", {}),
            **time,
        })
    partidas.sort(key=lambda p: p.get("fim_ts", 0), reverse=True)
    return partidas


def _bloco_metricas(plano: dict, medias_pos: dict) -> str:
    """Tabela 'antes → depois (delta)' de todas as métricas da rota, marcando a métrica-foco
    do plano. Todas as métricas da rota são 'maior = melhor', então delta>0 = melhora."""
    foco = plano.get("metrica")
    linhas = []
    for m, base in (plano.get("metricas_baseline") or {}).items():
        antes = base.get("valor")
        depois = medias_pos.get(m)
        label = METRIC_LABELS.get(m, m.upper().replace("_", " "))
        if m == foco:
            label += " (MÉTRICA-FOCO DO PLANO)"
        if antes is None or depois is None:
            linhas.append(f"- {label}: sem dados suficientes para comparar.")
            continue
        delta = depois - antes
        rumo = "subiu" if delta > 0 else ("caiu" if delta < 0 else "estável")
        linhas.append(
            f"- {label}: {round(antes, 2)} → {round(depois, 2)} "
            f"({delta:+.2f}, {rumo})."
        )
    return "\n".join(linhas) if linhas else "- (sem métricas de baseline registradas)"


def _bloco_partidas(partidas: list[dict]) -> str:
    """Detalha as partidas pós-plano (campeão + classe, resultado, KDA, CS/min, placar do
    time e composições) para o modelo cruzar com os movimentos das métricas."""
    if not partidas:
        return "(nenhuma partida nova nesta rota desde o plano)"
    blocos = []
    for i, p in enumerate(partidas[:_MAX_PARTIDAS_DETALHE], 1):
        resultado = "Vitória" if p["venceu"] else "Derrota"
        classes = f" [{', '.join(p['classes'])}]" if p.get("classes") else ""
        funcoes = f" — {p['funcoes_desc']}" if p.get("funcoes_desc") else ""
        placar = f"{p['abates_aliados']}–{p['abates_inimigos']} (seu time–inimigo)"
        aliados = ", ".join(p.get("aliados", [])) or "?"
        inimigos = ", ".join(p.get("inimigos", [])) or "?"
        blocos.append(
            f"Partida {i} — {p['campeao']}{classes}{funcoes}\n"
            f"  Resultado: {resultado}. Placar de abates: {placar}.\n"
            f"  Seu desempenho: KDA {p.get('kda')} ({p.get('kills')}/{p.get('deaths')}/"
            f"{p.get('assists')}), KP {p.get('kp')}%, CS/min {p.get('cs_min')}.\n"
            f"  Aliados: {aliados}.\n"
            f"  Inimigos: {inimigos}."
        )
    extra = ""
    if len(partidas) > _MAX_PARTIDAS_DETALHE:
        extra = f"\n(+{len(partidas) - _MAX_PARTIDAS_DETALHE} partida(s) mais antiga(s) omitida(s))"
    return "\n\n".join(blocos) + extra


def montar_contexto(plano: dict, perfil: dict, medias_pos: dict, n_pos: int,
                    partidas: list[dict]) -> str:
    """Monta o texto FACTUAL (números reais) que o modelo vai interpretar — nada de inventar
    estatísticas: tudo o que ele citar deve sair daqui."""
    rota = plano.get("posicao", "")
    rota_label = ROLE_LABELS.get(rota, rota)
    elo = (perfil.get("elo_oficial") or "").replace("_", " ")
    foco_label = plano.get("metrica_label", plano.get("metrica", ""))
    pct = round(progresso_metrica(plano) * 100)
    status_meta = ("META ATINGIDA" if meta_atingida(plano)
                   else f"{pct}% do caminho até o alvo")
    return f"""### CONTEXTO DA EVOLUÇÃO (dados reais — não invente números) ###
Jogador: {nome_exibicao(perfil.get('nick'))}
Rota: {rota_label} | Elo: {elo}
Plano criado em: {plano.get('criado_em')} | Partidas novas nesta rota desde então: {n_pos}
Comparação das métricas: {descrever_base_plano(plano)}.

Meta do plano: subir {foco_label} de {plano.get('valor_inicial')} para {plano.get('valor_alvo')} \
(referência do elo {str(plano.get('elo_alvo', '')).replace('_', ' ')}).
Progresso atual: {plano.get('valor_atual')} ({status_meta}).

### MÉTRICAS: ANTES (criação do plano) → DEPOIS (média das partidas novas) ###
{_bloco_metricas(plano, medias_pos)}

### PARTIDAS JOGADAS DESDE O PLANO (da mais recente para a mais antiga) ###
{_bloco_partidas(partidas)}
"""


_SISTEMA = """Você é o tutor de League of Legends do EloRise, acompanhando a EVOLUÇÃO de um \
jogador depois que ele começou a treinar com um plano. Sua missão nesta aba é dar um \
feedback humano e técnico sobre a evolução dele.

TOM (obrigatório em toda resposta):
- APOIO MORAL: comece reconhecendo o esforço, celebre o que melhorou e mantenha o jogador \
motivado mesmo quando os números caíram. Treinar dá trabalho — valide isso.
- CRÍTICA CONSTRUTIVA: aponte o que regrediu ou estagnou de forma honesta, mas sempre \
acompanhada de uma orientação prática do que fazer para corrigir.

ANÁLISE CAUSAL (o coração da sua resposta): para as métricas que SUBIRAM ou CAÍRAM, explique \
o PORQUÊ provável cruzando os dados do contexto:
- o campeão jogado em cada partida e suas CARACTERÍSTICAS de classe (ex.: um tanque/suporte \
naturalmente farma e dá menos dano que um atirador; um assassino tem KDA volátil);
- o resultado e o desempenho do TIME (placar de abates, vitória/derrota): em derrotas com o \
time atrás, métricas como ouro/min, dano e CS tendem a cair por motivos fora do controle do \
jogador — diga isso quando os dados sugerirem;
- a COMPOSIÇÃO das equipes (ex.: muito controle de grupo inimigo dificulta o farm; falta de \
engage no time afunda o KP);
- o elo, quando relevante para calibrar a expectativa.

REGRAS:
- Use APENAS os números do contexto. NUNCA invente métricas, nomes de campeões ou partidas.
- Seja concreto: relacione um movimento de métrica a partidas/campeões específicos do contexto \
("seu CS/min caiu nas duas derrotas como Leona, um suporte...").
- Quando houver poucas partidas novas, diga que a amostra ainda é pequena e evite conclusões \
duras.
- Não devolva perguntas socráticas aqui: esta aba é uma ANÁLISE, não um diálogo.
- Ao citar o nome do jogador, use APENAS o nome informado em "Jogador:" (já sem a tag) e \
escreva-o como texto normal — NUNCA em itálico/negrito e NUNCA com a tag após '#'.

FORMATO (Markdown, PT-BR, conciso):
1. Um parágrafo curto de abertura com apoio moral e o veredito geral da evolução.
2. **O que evoluiu** — bullets com a métrica e o porquê provável (ligado às partidas/campeões).
3. **O que precisa de atenção** — bullets com o que caiu/estagnou, o porquê e a correção prática.
4. Uma frase final de incentivo, ancorada no progresso rumo à meta do plano."""


def _llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY"),
    )


def gerar_insights_evolucao(plano: dict, perfil: dict, medias_pos: dict, n_pos: int,
                            partidas: list[dict]) -> str:
    """Gera o texto de insights (Markdown) sobre a evolução do jogador desde o plano.
    Lança exceção em caso de falha de rede/credenciais — o chamador decide como tratar."""
    contexto = montar_contexto(plano, perfil, medias_pos, n_pos, partidas)
    prompt = ChatPromptTemplate.from_messages([
        ("system", _SISTEMA),
        ("human", "{contexto}\n\nGere a análise de evolução seguindo o formato pedido."),
    ])
    cadeia = prompt | _llm() | StrOutputParser()
    return cadeia.invoke({"contexto": contexto})
