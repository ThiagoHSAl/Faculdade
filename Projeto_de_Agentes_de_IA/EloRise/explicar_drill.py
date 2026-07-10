"""
explicar_drill.py — Explicação sob demanda de UM exercício (drill) do plano de treino.

Quando o jogador clica no "?" ao lado de um drill, esta camada gera uma explicação CONCRETA
de COMO executar aquele exercício com o CAMPEÃO dele, na rota e métrica do plano. É uma
chamada única ao LLM (não o agente socrático), fundamentada na base de conhecimento
(características do campeão + conceitos táticos) para reduzir alucinação. Devolve Markdown.
"""
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from config import METRIC_LABELS, ROLE_LABELS
from base_conhecimento import caracteristicas_campeao, buscar, formatar_resultados

load_dotenv()


def _campeoes_do_plano(plano: dict) -> list[dict]:
    """Características (classe/papel) dos campeões de referência do plano (até 3)."""
    champs = plano.get("campeoes_referencia") or []
    infos = [caracteristicas_campeao(c) for c in champs[:3]]
    return [i for i in infos if i]


def _contexto_campeao(infos: list[dict]) -> str:
    if not infos:
        return ("Campeão: não identificado para esta rota — dê a explicação geral para a "
                "rota/classe, sem citar um campeão específico.")
    linhas = [f"- {i['nome']} ({i['funcoes_desc']})." for i in infos]
    return "Campeão(ões) que o jogador usa nesta rota:\n" + "\n".join(linhas)


_SISTEMA = """Você é um tutor de League of Legends. O jogador segue um plano de treino e quer \
saber COMO executar, na prática, UM exercício específico — com o campeão dele.

Explique de forma CONCRETA, ACIONÁVEL e curta:
- Conecte a explicação ao campeão do jogador (use a classe/papel e as habilidades quando \
fizer sentido) e à rota dele.
- Diga O QUE fazer no jogo, QUANDO fazer e COMO reconhecer/treinar (gatilhos visuais, \
timings, posicionamento).
- Sobre "pico de poder": costuma ser ao completar o 1º/2º item principal e em níveis-chave \
(ex.: nível 2/3/6, quando a ultimate fica disponível). Adapte ao tipo de campeão; NÃO invente \
números exatos de dano nem nomes de itens dos quais você não tenha certeza.
- Baseie-se no CONHECIMENTO DE APOIO fornecido; se faltar um dado específico, fale em termos \
gerais (ex.: "seu primeiro item de dano") em vez de inventar.

Regras: responda em PT-BR, tom de mentor direto e encorajador. NÃO use emojis. No máximo \
~5 frases curtas OU 4 bullets. Não repita o enunciado do exercício — vá direto ao COMO."""


def _llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY"),
    )


def explicar_drill(plano: dict, passo: dict) -> str:
    """Gera a explicação (Markdown) de como executar `passo` no contexto de `plano`
    (campeão, rota, métrica). Lança exceção em falha de rede/credenciais — o chamador trata."""
    infos = _campeoes_do_plano(plano)
    rota = ROLE_LABELS.get(plano.get("posicao", ""), plano.get("posicao", ""))
    metrica = plano.get("metrica_label") or METRIC_LABELS.get(
        plano.get("metrica", ""), plano.get("metrica", ""))
    submetas = "; ".join(s.get("descricao", "") for s in passo.get("submetas", []))

    # Conhecimento de apoio: conceito do drill + características/habilidades do campeão.
    termos = passo.get("descricao", "")
    if infos:
        termos += " " + " ".join(i["nome"] for i in infos)
    apoio = formatar_resultados(buscar(f"{termos} {metrica} {rota}", k=4))

    contexto = (
        f"Rota: {rota}.\n"
        f"{_contexto_campeao(infos)}\n"
        f"Métrica em treino: {metrica} "
        f"(meta: subir de {plano.get('valor_inicial')} para {plano.get('valor_alvo')}).\n"
        f"EXERCÍCIO a explicar:\n"
        f"  Objetivo: {passo.get('descricao', '')}\n"
        + (f"  Passos sugeridos: {submetas}\n" if submetas else "")
        + f"\n{apoio}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", _SISTEMA),
        ("human", "{contexto}\n\nExplique COMO executar este exercício, específico para o "
                  "campeão e a rota do jogador."),
    ])
    cadeia = prompt | _llm() | StrOutputParser()
    return cadeia.invoke({"contexto": contexto})
