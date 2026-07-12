import streamlit as st
import requests
import pandas as pd
import altair as alt
import html
import os
import time
import base64
from io import BytesIO
from contextlib import contextmanager
from PIL import Image
from datetime import datetime, timedelta
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# Ponte de segredos (Streamlit Community Cloud): copia a seção [env] do secrets para
# variáveis de ambiente ANTES dos imports do projeto — config.py/riot_client/rag leem
# RIOT_API_KEY, GEMINI_API_KEY etc. no import, e no cloud não existe arquivo .env.
try:
    for _k, _v in dict(st.secrets.get("env", {})).items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass

# Importando a lógica isolada da Feature 3
from tutor_interativo import buscar_perfil_e_formatar, usuario_desistiu, pergunta_factual, obter_cadeia_tutor, obter_historico, semear_memoria, semear_plano, obter_dados_jogador, responder_tutor, _benchmarks_rota_cached, invalidar_cache_jogador, descrever_base_comparacao, analisar_partida_texto, analisar_padroes_texto
from plano_treino import gerar_plano_treino, atualizar_valor_atual, progresso_metrica, marcar_passo, marcar_submeta, registrar_medicao, meta_atingida, descrever_base_plano, proxima_metrica, trocar_drills, assinatura_plano, avancar_metrica
from generate_stats import agregar_metricas_rota_periodo
from base_conhecimento import erros_comuns_do_elo
from insights_evolucao import coletar_partidas_pos_plano, gerar_insights_evolucao
from explicar_drill import explicar_drill
from persistencia import (carregar_sessao, salvar_sessao, limpar_sessao, excluir_jogador,
                          listar_jogadores, excluir_usuario)
import auth
import legal
from riot_client import RiotClient
import analise_partidas
import viz_partidas
import plotly.graph_objects as go
from config import BENCHMARKS_API_URL, ROLE_LABELS, METRIC_LABELS, SERVIDORES, FILAS, FILA_PADRAO, nome_exibicao

# Configuração da página do Streamlit
_DIR_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _carregar_icone():
    """Favicon da aba do navegador (cai no favicon padrão se o PNG não existir)."""
    caminho = os.path.join(_DIR_ASSETS, "icon.png")
    try:
        return Image.open(caminho)
    except Exception:
        return None


def _carregar_logo_svg() -> str:
    """Lê o logo (assets/logo.svg) — fonte única da identidade visual, reaproveitada no
    favicon. Regenerado por assets/gerar_monograma.py."""
    try:
        with open(os.path.join(_DIR_ASSETS, "logo.svg"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'></svg>"


_LOGO_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(
    _carregar_logo_svg().strip().encode("utf-8")
).decode("ascii")


def _logo_svg(tamanho: int = 120) -> str:
    """Emblema EloRise (monograma serifado 'ER' + swoosh dourado) como <img> com data
    URI — renderiza de forma confiável dentro do st.markdown, em qualquer tamanho."""
    return (
        f"<img class='er-logo' src='{_LOGO_DATA_URI}' "
        f"width='{tamanho}' height='{tamanho}' alt='EloRise' />"
    )


st.set_page_config(page_title="EloRise", page_icon=_carregar_icone(), layout="wide")


def _injetar_estilo():
    """Tema visual Hextech (paleta do LoL): fundo escuro, acentos em dourado/azul,
    cards e componentes estilizados. Centraliza toda a identidade visual num só lugar."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Marcellus&display=swap');

        :root {
            --gold: #C8AA6E;
            --gold-bright: #F0E6D2;
            --gold-dark: #785A28;
            --teal: #0AC8B9;
            --bg-0: #070D14;
            --bg-1: #0E1822;
            --bg-2: #15232F;
            --bg-3: #1B2C3B;
            --border: #243B4F;
            --text: #E8EDF2;
            --muted: #A9BCCB;
            --green: #2DD4A7;
            --red: #E06B6B;
        }

        /* Fundo com leve brilho hextech no topo */
        .stApp {
            background:
                radial-gradient(1100px 520px at 50% -260px, rgba(16,60,90,.55) 0%, rgba(16,48,71,0) 60%),
                linear-gradient(180deg, #0B1825 0%, var(--bg-0) 100%) fixed;
            font-family: 'Inter', system-ui, sans-serif;
        }

        /* Garante texto claro em todos os elementos de texto */
        .stApp, .stMarkdown, p, span, li, label,
        [data-testid="stWidgetLabel"] p, .stChatMessage p {
            color: var(--text);
        }
        [data-testid="stCaptionContainer"], .stCaption, small { color: var(--muted) !important; }

        /* Títulos — Marcellus dá um ar editorial/épico */
        h1, h2, h3, h4 { font-family: 'Marcellus', 'Inter', serif !important; letter-spacing: .4px; }
        h1 {
            font-weight: 700 !important;
            background: linear-gradient(92deg, var(--gold-bright), var(--gold) 55%, var(--gold-dark));
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2, h3 { color: var(--gold) !important; font-weight: 600 !important; }

        /* Régua horizontal com acento dourado no centro */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, var(--gold-dark) 20%, var(--gold) 50%, var(--gold-dark) 80%, transparent) !important;
            opacity: .7;
        }

        [data-testid="stHeader"] { background: transparent; }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] h1 { font-size: 1.5rem; }

        /* Cartões de métrica com acento dourado e brilho no hover */
        [data-testid="stMetric"] {
            background: linear-gradient(160deg, var(--bg-2), var(--bg-1));
            border: 1px solid var(--border);
            border-left: 3px solid var(--gold);
            border-radius: 10px;
            padding: 14px 16px;
            transition: border-color .15s ease, transform .15s ease;
        }
        [data-testid="stMetric"]:hover { border-color: var(--gold-dark); transform: translateY(-2px); }
        [data-testid="stMetricLabel"] p { color: var(--muted) !important; font-weight: 600; text-transform: uppercase; font-size: .72rem; letter-spacing: .5px; }
        [data-testid="stMetricValue"] { color: var(--gold-bright) !important; font-weight: 700; }

        /* Container com borda (cards de partida) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            border-color: var(--border) !important;
            background: linear-gradient(160deg, rgba(27,44,59,.45), rgba(14,24,34,.45));
            transition: border-color .15s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: var(--gold-dark) !important; }

        /* Abas */
        [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid var(--border); }
        [data-baseweb="tab"] {
            background: transparent; color: var(--muted); font-weight: 600;
            font-family: 'Marcellus', serif; font-size: 1.02rem; padding: 4px 10px;
        }
        [data-baseweb="tab"]:hover { color: var(--gold); }
        [data-baseweb="tab"][aria-selected="true"] { color: var(--gold-bright); }
        [data-baseweb="tab-highlight"] { background: var(--gold) !important; height: 3px !important; }

        /* Botões */
        .stButton button, .stFormSubmitButton button, .stDownloadButton button {
            border: 1px solid var(--gold-dark);
            border-radius: 8px;
            font-weight: 600;
            color: var(--gold);
            background: rgba(120,90,40,.08);
            transition: all .15s ease;
        }
        .stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {
            border-color: var(--gold);
            color: var(--gold-bright);
            background: rgba(200,170,110,.12);
            box-shadow: 0 0 12px -2px var(--gold-dark);
        }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] {
            background: linear-gradient(90deg, var(--gold-dark), var(--gold));
            color: #0A0A0A;
            border: none;
        }
        .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover {
            filter: brightness(1.1);
            box-shadow: 0 0 16px -2px var(--gold);
            color: #0A0A0A;
        }
        /* X vermelho de excluir análise salva (cards da tela de busca):
           quadradinho compacto, centrado na altura do botão do card (2.5rem) */
        [class*="st-key-excluir_"] .stButton button {
            color: #E2504A;
            border-color: rgba(226,80,74,.45);
            background: rgba(226,80,74,.08);
            font-weight: 700;
            min-height: 0;
            height: 1.6rem;
            width: 1.6rem;
            padding: 0;
            line-height: 1;
            font-size: .8rem;
            margin-top: .45rem;
        }
        [class*="st-key-excluir_"] .stButton button:hover {
            color: #FF6B64;
            border-color: #E2504A;
            background: rgba(226,80,74,.15);
            box-shadow: 0 0 12px -2px rgba(226,80,74,.6);
        }

        /* Barra de progresso */
        .stProgress div[role="progressbar"] > div,
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--gold-dark), var(--gold)) !important;
        }

        /* Inputs / selects */
        [data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="base-input"] {
            background: var(--bg-1) !important;
            border-radius: 8px;
            border-color: var(--border) !important;
        }
        [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
            border-color: var(--gold) !important;
        }

        /* Chat e expander */
        [data-testid="stChatMessage"] {
            background: var(--bg-1);
            border: 1px solid var(--border);
            border-radius: 12px;
        }
        [data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 10px; background: rgba(14,24,34,.4); }

        /* Caixas de alerta no tom do tema (acento à esquerda) */
        [data-testid="stAlert"] {
            border-radius: 10px;
            border-left: 4px solid var(--gold);
            background: var(--bg-2) !important;
        }
        [data-testid="stAlert"] * { color: var(--text) !important; }

        /* Cabeçalho-herói reutilizável */
        .hero {
            padding: 6px 0 2px;
        }
        .hero h1 {
            font-size: 2.6rem; margin-bottom: 2px;
        }
        .hero .sub {
            color: var(--muted); font-size: 1rem; letter-spacing: .3px;
        }
        .hero .rule {
            margin-top: 12px; height: 2px; width: 120px;
            background: linear-gradient(90deg, var(--gold), transparent);
            border-radius: 2px;
        }

        /* ===== Tela inicial (splash) — nome + logo + slogan animados ===== */
        .er-splash {
            position: fixed; inset: 0; z-index: 9999;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 18px; text-align: center;
            background:
                radial-gradient(900px 520px at 50% 30%, rgba(16,60,90,.55) 0%, rgba(16,48,71,0) 62%),
                linear-gradient(180deg, #0B1825 0%, var(--bg-0) 100%);
            animation: er-splash-out .6s ease 3s forwards;
        }
        .er-splash .er-logo-wrap {
            opacity: 0; transform: translateY(18px) scale(.85);
            filter: drop-shadow(0 0 0 rgba(200,170,110,0));
            animation: er-logo-in .9s cubic-bezier(.2,.8,.2,1) .15s forwards,
                       er-logo-glow 2.6s ease-in-out 1s infinite;
        }
        .er-splash .er-name {
            font-family: 'Marcellus', serif; font-weight: 700;
            font-size: clamp(2.6rem, 7vw, 4.4rem); line-height: 1; letter-spacing: 1px;
            background: linear-gradient(92deg, var(--gold-bright), var(--gold) 55%, var(--gold-dark));
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
            opacity: 0; transform: translateY(16px);
            animation: er-rise-in .8s ease .55s forwards;
        }
        .er-splash .er-name b { font-weight: 700; color: var(--gold-bright); -webkit-text-fill-color: var(--gold-bright); }
        .er-splash .er-slogan {
            color: var(--muted); font-size: clamp(.95rem, 2.4vw, 1.25rem); letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0; transform: translateY(12px);
            animation: er-rise-in .8s ease .95s forwards;
        }
        .er-splash .er-line {
            height: 2px; width: 0; border-radius: 2px;
            background: linear-gradient(90deg, transparent, var(--gold) 50%, transparent);
            animation: er-line-grow .9s ease 1.2s forwards;
        }
        @keyframes er-logo-in {
            from { opacity: 0; transform: translateY(18px) scale(.85); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes er-logo-glow {
            0%,100% { filter: drop-shadow(0 0 6px rgba(200,170,110,.25)); }
            50%     { filter: drop-shadow(0 0 22px rgba(200,170,110,.55)); }
        }
        @keyframes er-rise-in { to { opacity: 1; transform: translateY(0); } }
        @keyframes er-line-grow { to { width: min(260px, 60vw); } }
        @keyframes er-splash-out { to { opacity: 0; visibility: hidden; } }

        /* ===== Overlay de carregamento — logo EloRise pulsando (indo e voltando), sem slogan.
           Mesma identidade da splash; usado sempre que algo está sendo processado. ===== */
        .er-loading {
            position: fixed; inset: 0; z-index: 9998;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 16px; text-align: center;
            background:
                radial-gradient(900px 520px at 50% 38%, rgba(16,60,90,.45) 0%, rgba(16,48,71,0) 62%),
                rgba(8, 16, 26, .78);
            backdrop-filter: blur(3px);
            animation: er-loading-fade .35s ease forwards;
        }
        /* Variante embutida: ocupa só o espaço do conteúdo (ex.: Panorama do Meta),
           sem cobrir nem travar a tela inteira. */
        .er-loading-inline {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            gap: 14px; text-align: center;
            padding: 56px 0 40px;
            animation: er-loading-fade .35s ease forwards;
        }
        .er-loading .er-logo-wrap,
        .er-loading-inline .er-logo-wrap {
            animation: er-load-bob 1.6s ease-in-out infinite,
                       er-logo-glow 2.2s ease-in-out infinite;
        }
        .er-loading .er-loading-text,
        .er-loading-inline .er-loading-text {
            color: var(--muted); font-size: 1rem; letter-spacing: 1.5px;
            text-transform: uppercase;
            opacity: .85;
            animation: er-load-pulse 1.6s ease-in-out infinite;
        }
        /* "indo e voltando": o emblema sobe e desce suavemente em loop. */
        @keyframes er-load-bob {
            0%,100% { transform: translateY(10px) scale(.94); }
            50%     { transform: translateY(-10px) scale(1.04); }
        }
        @keyframes er-load-pulse { 0%,100% { opacity: .45; } 50% { opacity: .95; } }
        @keyframes er-loading-fade { from { opacity: 0; } to { opacity: 1; } }

        /* ===== Cabeçalho de marca (logo + nome + slogan) ===== */
        .er-brand { display: flex; align-items: center; gap: 16px; padding: 6px 0 2px; }
        .er-brand .er-logo { flex: 0 0 auto; filter: drop-shadow(0 0 10px rgba(200,170,110,.18)); }
        .er-brand .er-name {
            font-family: 'Marcellus', serif; font-weight: 700;
            font-size: 2.6rem; line-height: 1;
            background: linear-gradient(92deg, var(--gold-bright), var(--gold) 55%, var(--gold-dark));
            -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        }
        .er-brand .er-slogan { color: var(--muted); font-size: 1rem; letter-spacing: .3px; margin-top: 4px; }
        .er-brand .rule { margin-top: 10px; height: 2px; width: 120px; border-radius: 2px;
            background: linear-gradient(90deg, var(--gold), transparent); }
        /* Marca compacta na barra lateral */
        .er-brand-mini { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
        .er-brand-mini .er-name { font-family: 'Marcellus', serif; font-size: 1.4rem; color: var(--gold-bright); }

        /* Botão de ajuda "?" do plano: inline, logo após o texto do passo (não no canto) */
        [class*="st-key-ajudalinha_"] {
            flex-direction: row !important;
            align-items: center !important;
            gap: 0.4rem !important;
        }
        [class*="st-key-ajudalinha_"] > [data-testid="stElementContainer"]:first-child {
            flex: 0 1 auto; min-width: 0;
        }
        [class*="st-key-ajudalinha_"] > [data-testid="stElementContainer"]:last-child {
            flex: 0 0 auto; width: auto !important;
        }
        [class*="st-key-ajudalinha_"] .stButton button {
            min-height: 1.6rem; height: 1.6rem; width: 1.6rem;
            padding: 0; border-radius: 50%; line-height: 1;
            display: inline-flex; align-items: center; justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


_injetar_estilo()


def _hero(titulo: str, subtitulo: str = ""):
    """Cabeçalho principal estilizado (título com gradiente dourado + subtítulo + régua)."""
    sub = f"<div class='sub'>{html.escape(subtitulo)}</div>" if subtitulo else ""
    st.markdown(
        f"<div class='hero'><h1>{html.escape(titulo)}</h1>{sub}<div class='rule'></div></div>",
        unsafe_allow_html=True,
    )


def _tela_inicial():
    """Splash de abertura: somente logo + nome (EloRise) + slogan, com animação de
    entrada. Renderizada uma única vez por sessão, antes da tela de pesquisa."""
    st.markdown(
        f"""
        <div class="er-splash">
            <div class="er-logo-wrap">{_logo_svg(132)}</div>
            <div class="er-name">Elo<b>Rise</b></div>
            <div class="er-line"></div>
            <div class="er-slogan">Tutoria Inteligente para League of Legends</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def _carregando(texto: str = "Carregando", inline: bool = False):
    """Substitui st.spinner: enquanto o bloco roda, exibe o emblema EloRise pulsando
    (mesma animação da splash, sem slogan), indicando que o sistema está processando.
    Nunca mostra nomes de funções internas.

    inline=False → overlay em tela cheia (bloqueia a interação).
    inline=True  → ocupa só o espaço do conteúdo, sem travar a tela inteira."""
    classe = "er-loading-inline" if inline else "er-loading"
    tamanho = 72 if inline else 84
    ph = st.empty()
    ph.markdown(
        f"""
        <div class="{classe}">
            <div class="er-logo-wrap">{_logo_svg(tamanho)}</div>
            <div class="er-loading-text">{html.escape(texto)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        ph.empty()


def _cabecalho_marca():
    """Cabeçalho de marca: logo + 'EloRise' + slogan, lado a lado (tela de pesquisa)."""
    st.markdown(
        f"""
        <div class="er-brand">
            <div class="er-logo">{_logo_svg(72)}</div>
            <div>
                <div class="er-name">EloRise</div>
                <div class="er-slogan">Tutoria Inteligente para League of Legends</div>
                <div class="rule"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def _aquecer_base_conhecimento() -> bool:
    """Carrega o índice semântico do RAG (cache em disco) uma vez por sessão — NUNCA o
    constrói aqui (a construção é offline via `python rag.py`, para não travar a sessão
    nem gastar a cota de embeddings). Se não houver índice, a ferramenta cai na busca por
    palavra-chave (zero cota)."""
    try:
        import rag
        return rag.carregar_indice() is not None
    except Exception:
        return False

@st.cache_data(ttl=86400, show_spinner=False)
def _versao_ddragon() -> str:
    """Versão mais recente do Data Dragon, cacheada por 24h (uma chamada de rede por
    dia, não uma por rerun). Exceção não entra no cache — o fallback fica no chamador."""
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    return requests.get(url, timeout=5).json()[0]


def obter_versao_mais_recente() -> str:
    """Busca a versão mais recente do Data Dragon (compartilhada entre API e App)."""
    try:
        return _versao_ddragon()
    except Exception as e:
        print(f"Erro ao buscar versão, usando fallback: {e}")
        return "14.11.1" # Fallback seguro

@st.cache_data(ttl=3600, show_spinner=False)
def _dados_panorama(elo: str, fila: str = FILA_PADRAO) -> dict:
    """Top campeões por rota do elo/fila, cacheado por 1h (o meta muda por patch, não por
    rerun). Erros de rede não entram no cache — o chamador trata e tenta de novo."""
    resp = requests.get(f"{BENCHMARKS_API_URL}/panorama-meta/{elo}",
                        params={"fila": fila}, timeout=10)
    resp.raise_for_status()
    return resp.json()


@st.fragment
def renderizar_panorama_meta():
    """Fragment: trocar o elo (ou interagir com o resto da tela) reroda só este bloco —
    o rerun de um clique fora daqui não paga o render do panorama, e vice-versa."""
    versao_atual = obter_versao_mais_recente()
    st.subheader("Panorama do Meta")
    
    # Seleção de Elo (largura contida). O emblema do elo é embutido DENTRO do seletor e em
    # CADA opção da lista, via CSS dinâmico com data URIs em cache (ver emblema_elo_data_uri).
    # A fila é lida ANTES de montar a lista de elos: só a Normal atribui o jogador ao próprio
    # elo solo/duo, então só nela existe o bucket UNRANKED (quem não tem rank). A fila é
    # renderizada primeiro para que a troca reflita na lista de elos no mesmo rerun.
    col_fila, col_elo, _ = st.columns([1.2, 1.5, 1.8])
    with col_fila:
        fila_selecionada = st.selectbox(
            "Fila:", list(FILAS.keys()),
            format_func=lambda f: FILAS[f]["label"], key="meta_fila",
        )
    elos = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD",
            "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
    if fila_selecionada == "normal":
        elos = ["UNRANKED"] + elos  # UNRANKED no topo da lista (antes de Iron)
    # Se o elo memorizado saiu da lista (ex.: estava em UNRANKED e trocou de fila),
    # reatribui ao 1º elo válido. NÃO usar pop(): remover a chave deixa o baseweb exibindo
    # o rótulo ANTIGO ("Sem Rank") enquanto o backend já caiu p/ Iron — o valor e o texto
    # ficam dessincronizados. Setar um valor válido força o rótulo a acompanhar.
    if st.session_state.get("meta_elo") not in elos:
        st.session_state["meta_elo"] = elos[0]
    with col_elo:
        elo_selecionado = st.selectbox(
            "Selecione o Elo para ver o Meta:", elos,
            format_func=_fmt_elo, key="meta_elo",
        )

    # O popover da lista é portado pro <body> (fora do .st-key). Para aplicar emblema/identidade
    # SÓ na lista do elo (e não no seletor de Servidor, que também tem 10 opções), escopo por
    # `body:has(.st-key-meta_elo input[aria-expanded="true"])` — verdadeiro apenas com o dropdown
    # de elo aberto, quando o único popover no DOM é justamente o dele.
    op = ('body:has(.st-key-meta_elo input[aria-expanded="true"]) '
          'div[data-baseweb="popover"] li[role="option"]')
    # IMPORTANTE: casar o emblema pelo ID da opção, NÃO por posição (:nth-child/:nth-of-type).
    # O baseweb VIRTUALIZA a lista: renderiza só ~10 <li> por vez (absolute + top:Npx) e os
    # RECICLA ao rolar. Com seletor posicional, o <li> na k-ésima posição visível recebia o
    # emblema k — então, ao rolar, cada opção pegava o emblema da de cima (o bug relatado:
    # "challenger com ícone de GM"). O baseweb dá a cada opção id="{prefixo}-{índiceLógico}";
    # o índice é ESTÁVEL (não muda com o scroll). `[id$="-{i}"]` casa exatamente a opção i
    # (o "-" antes do número evita ambiguidade: "...-1" não casa "...-10"/"...-11"). Verificado
    # com scroll no Streamlit 1.57 (produção): mapeamento 100% correto, inclusive Challenger.
    regras_opcoes = "".join(
        f'{op}[id$="-{i}"] {{ background-image: url("{emblema_elo_data_uri(e, 80)}") !important; }}'
        for i, e in enumerate(elos)
    )
    st.markdown(
        f"""
        <style>
        /* Valor fechado: emblema grande à esquerda + identidade dourada/Marcellus */
        .st-key-meta_elo div[data-baseweb="select"] > div:first-child {{
            min-height: 60px;
            padding-left: 68px !important;
            align-items: center;
            background: url('{emblema_elo_data_uri(elo_selecionado, 144)}') 12px center / 46px 46px no-repeat,
                        var(--bg-1) !important;
        }}
        .st-key-meta_elo div[data-baseweb="select"] > div:first-child div[value],
        .st-key-meta_elo div[data-baseweb="select"] > div:first-child div {{
            font-family: 'Marcellus', serif !important;
            color: var(--gold) !important;
            font-size: 1.35rem !important;
            font-weight: 600;
        }}
        /* Lista aberta (só do elo): identidade dourada/Marcellus + espaço p/ o emblema */
        {op} {{
            padding-left: 58px !important;
            min-height: 50px;
            background-repeat: no-repeat !important;
            background-position: 16px center !important;
            background-size: 36px 36px !important;
        }}
        {op}, {op} div {{
            font-family: 'Marcellus', serif !important;
            color: var(--gold) !important;
            font-size: 1.18rem !important;
        }}
        {regras_opcoes}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Busca da API. O loader é embutido (inline=True) para sinalizar o carregamento
    # do panorama sem cobrir nem travar o resto da tela.
    try:
        with _carregando(f"Carregando o meta de {_fmt_elo(elo_selecionado)}", inline=True):
            data = _dados_panorama(elo_selecionado, fila_selecionada)
            mapa_itens = obter_mapa_itens_nome_id(versao_atual)  # nome -> id, p/ ícones da build

        # data pode ser {"mensagem": ...} quando a fila não tem amostra nesse elo.
        if isinstance(data, dict) and data.get("mensagem"):
            st.info(f"Sem dados de {FILAS[fila_selecionada]['label']} para {_fmt_elo(elo_selecionado)} ainda. "
                    "As filas Flex e Normal estão sendo coletadas e vão preencher com o tempo.")
            return

        # Grid para as 5 rotas (Top 10 por rota, com winrate, amostra e itens frequentes)
        st.caption(f"Top 10 campeões por rota ({FILAS[fila_selecionada]['label']}), por taxa de vitória.")
        cols = st.columns(5)
        for i, posicao in enumerate(["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]):
            with cols[i]:
                st.markdown(_header_lane(posicao), unsafe_allow_html=True)
                for pos, champ in enumerate(data.get(posicao, []), start=1):
                    st.markdown(_card_campeao_meta(champ, versao_atual, mapa_itens, pos),
                                unsafe_allow_html=True)
    except requests.exceptions.RequestException as e:
        st.error(f"Servidor de Meta offline. Detalhes: {e}")

# ──────────────────────────────────────────────
# Histórico de partidas (cards estilo op.gg)
# ──────────────────────────────────────────────
DDRAGON = "https://ddragon.leagueoflegends.com/cdn"

@st.cache_data(ttl=86400, show_spinner=False)
def obter_mapa_campeoes(versao: str) -> dict:
    """Mapa championId(str) -> arquivo de imagem (resolve casos como Wukong/MonkeyKing)."""
    try:
        url = f"{DDRAGON}/{versao}/data/pt_BR/champion.json"
        data = requests.get(url, timeout=10).json()["data"]
        return {str(info["key"]): info["image"]["full"] for info in data.values()}
    except Exception:
        return {}

@st.cache_data(ttl=86400, show_spinner=False)
def obter_mapa_itens_nome_id(versao: str) -> dict:
    """Mapa nome_do_item -> id (locale pt_BR). O cache do panorama guarda a build por NOME,
    mas a URL de imagem do Data Dragon usa o id."""
    try:
        url = f"{DDRAGON}/{versao}/data/pt_BR/item.json"
        data = requests.get(url, timeout=10).json()["data"]
        return {info["name"]: item_id for item_id, info in data.items()}
    except Exception:
        return {}

@st.cache_data(ttl=86400, show_spinner=False)
def obter_meta_itens(versao: str) -> dict:
    """item_id(str) -> {componente, tags, nome, ouro} (pt_BR). `componente` = constrói em
    outro item (campo `into` não-vazio no Data Dragon) — usado para esconder peças de
    receita na build; `ouro` (custo total) e `nome` alimentam o tooltip do item."""
    try:
        url = f"{DDRAGON}/{versao}/data/pt_BR/item.json"
        data = requests.get(url, timeout=10).json()["data"]
        return {iid: {"componente": bool(info.get("into")),
                      "tags": info.get("tags", []), "nome": info.get("name", ""),
                      "ouro": info.get("gold", {}).get("total", 0)}
                for iid, info in data.items()}
    except Exception:
        return {}

def url_icone_campeao(champ_id, versao, mapa) -> str:
    arquivo = mapa.get(str(champ_id))
    if not arquivo:
        return "https://raw.communitydragon.org/latest/game/assets/characters/none.png"
    return f"{DDRAGON}/{versao}/img/champion/{arquivo}"

def url_item(item_id, versao) -> str:
    return f"{DDRAGON}/{versao}/img/item/{item_id}.png"

def tempo_atras(ts_ms) -> str:
    if not ts_ms:
        return ""
    delta = time.time() - ts_ms / 1000
    dias = int(delta // 86400)
    if dias >= 1:
        return f"há {dias} dia{'s' if dias > 1 else ''}"
    horas = int(delta // 3600)
    if horas >= 1:
        return f"há {horas}h"
    return f"há {max(1, int(delta // 60))}min"

def _fmt_elo(elo) -> str:
    """Humaniza identificadores de elo da Riot p/ exibição (ex.: 'MASTER_I' -> 'Master I',
    'DIAMOND_IV' -> 'Diamond IV'). Mantém a divisão em romano e evita vazar a string
    técnica (maiúsculas com underscore) na interface."""
    if not elo:
        return "—"
    if str(elo).upper() in ("UNRANKED", "UNRANKED_I"):
        return "Sem Rank"
    romanos = {"I", "II", "III", "IV"}
    partes = [
        tok.upper() if tok.upper() in romanos else tok.capitalize()
        for tok in str(elo).replace("_", " ").split()
    ]
    return " ".join(partes)

def _img_tag(url, size, title="") -> str:
    t = f" title='{html.escape(title)}'" if title else ""
    return (f"<img src='{url}' width='{size}' height='{size}'{t} "
            f"style='border-radius:4px;vertical-align:middle'>")

# Ícones de posição que o próprio cliente do LoL usa (CommunityDragon).
_ICONE_LANE = {"TOP": "top", "JUNGLE": "jungle", "MIDDLE": "middle",
               "BOTTOM": "bottom", "UTILITY": "utility"}

def url_icone_lane(posicao) -> str:
    nome = _ICONE_LANE.get(posicao, "fill")
    return ("https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-parties/"
            f"global/default/icon-position-{nome}.png")

def url_emblema_elo(tier) -> str:
    """Emblema do tier ranqueado (Ferro..Desafiante) hospedado no CommunityDragon."""
    t = str(tier).lower()
    return ("https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/"
            f"global/default/images/ranked-emblem/emblem-{t}.png")

@st.cache_data(ttl=604800, show_spinner=False)
def emblema_elo_data_uri(tier: str, tamanho: int = 96) -> str:
    """Baixa o emblema do elo UMA vez (cache por 7 dias), redimensiona com Pillow e devolve
    como data URI base64. Evita refetch a cada rerun, some com o flicker e deixa o CSS leve.
    Cai na URL externa se algo falhar."""
    try:
        # UNRANKED não existe no CommunityDragon: usa o emblema local (assets/), mesmo
        # pipeline de recorte/thumbnail dos demais. Sem rede → sem 404/flicker.
        if str(tier).upper() in ("UNRANKED", "UNRANKED_I"):
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "assets", "unranked_emblem.webp")
            img = Image.open(caminho).convert("RGBA")
        else:
            resp = requests.get(url_emblema_elo(tier), timeout=6)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGBA")
        bbox = img.getbbox()  # recorta a moldura transparente p/ o brasão preencher a caixa
        if bbox:
            img = img.crop(bbox)
        img.thumbnail((tamanho, tamanho))
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return url_emblema_elo(tier)

def _header_lane(posicao) -> str:
    """Cabeçalho da rota: ícone de lane num anel dourado + nome da rota."""
    icone = _img_tag(url_icone_lane(posicao), 18)
    label = ROLE_LABELS.get(posicao, posicao)
    return (f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;"
            f"padding-bottom:8px;border-bottom:1px solid var(--border)'>"
            f"<span style='display:inline-flex;align-items:center;justify-content:center;"
            f"width:30px;height:30px;background:var(--bg-2);border:1px solid var(--gold-dark);"
            f"border-radius:50%'>{icone}</span>"
            f"<span style='font-weight:600;font-size:.98rem;color:var(--gold)'>{html.escape(str(label))}</span>"
            f"</div>")

def _card_campeao_meta(champ, versao, mapa_itens, pos) -> str:
    """Card compacto do panorama: rank + ícone do campeão + winrate (colorido) + amostra
    + os 5 itens mais comprados (ordem de popularidade — o hover diz a posição; NÃO é
    build recomendada)."""
    icone = (f"<img src='{DDRAGON}/{versao}/img/champion/{champ['campeao']}.png' "
             f"width='40' height='40' style='border-radius:50%;border:2px solid var(--border);"
             f"object-fit:cover;flex:none'>")
    itens_html = "".join(
        _img_tag(url_item(mapa_itens[n], versao), 22,
                 title=f"{i}º item mais comprado: {n}")
        for i, n in enumerate(
            [n for n in champ.get("top_5_itens", []) if n in mapa_itens], start=1)
    )
    # As 2 botas mais compradas vêm num ranking próprio do cache ('top_2_botas');
    # caches antigos ainda não têm o campo — aí o grupo simplesmente não aparece.
    botas_html = "".join(
        _img_tag(url_item(mapa_itens[n], versao), 22,
                 title=f"{i}ª bota mais comprada: {n}")
        for i, n in enumerate(
            [n for n in champ.get("top_2_botas", []) if n in mapa_itens], start=1)
    )
    # Cada grupo (rótulo + ícones) é um inline-flex atômico: se faltar largura, o grupo
    # de botas quebra INTEIRO para a linha de baixo — o rótulo nunca separa dos ícones.
    grupo_itens = ("<span style='display:inline-flex;align-items:center;gap:2px;flex:none'>"
                   "<span style='font-size:.72rem;color:var(--muted);margin-right:3px'>"
                   f"Top 5 itens:</span>{itens_html}</span>")
    grupo_botas = ""
    if botas_html:
        grupo_botas = ("<span style='display:inline-flex;align-items:center;gap:2px;"
                       "flex:none;margin-left:8px'>"
                       "<span style='font-size:.72rem;color:var(--muted);margin-right:3px'>"
                       f"Botas:</span>{botas_html}</span>")
    wr = champ["winrate"]
    wr_cor = "#2DD4A7" if wr >= 52 else "#E8C265" if wr >= 49 else "#E06B6B"
    return (
        f"<div style='display:flex;align-items:center;gap:9px;padding:7px 9px;margin-bottom:7px;"
        f"border:1px solid var(--border);border-radius:10px;"
        f"background:linear-gradient(160deg,rgba(27,44,59,.4),rgba(14,24,34,.4))'>"
        f"<div style='color:var(--gold);font-weight:700;font-size:.8rem;width:16px;"
        f"text-align:center;flex:none'>{pos}</div>"
        f"{icone}"
        f"<div style='flex:1;min-width:0'>"
        f"<div style='font-weight:600;font-size:.94rem;color:var(--text);white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis'>{html.escape(str(champ['campeao']))}</div>"
        f"<div style='font-size:.82rem'><span style='color:{wr_cor};font-weight:600'>{wr}%</span>"
        f"<span style='color:var(--muted)'> · {champ.get('amostra', 0)} jogos</span></div>"
        f"<div style='display:flex;margin-top:4px;flex-wrap:wrap;align-items:center;"
        f"row-gap:3px'>{grupo_itens}{grupo_botas}</div>"
        f"</div>"
        f"</div>"
    )

def _roster_html(participantes, versao, mapa, puuid) -> str:
    linhas = []
    for p in participantes:
        nome = html.escape(p["nick"])
        eu = p["puuid"] == puuid
        cor_nome = "var(--gold-bright)" if eu else "var(--muted)"
        peso = "700" if eu else "400"
        icone = _img_tag(url_icone_campeao(p["champion_id"], versao, mapa), 18)
        linhas.append(
            f"<div style='display:flex;align-items:center;gap:5px;max-width:118px'>"
            f"{icone}<span style='font-size:0.72rem;color:{cor_nome};font-weight:{peso};"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{nome}</span></div>"
        )
    return f"<div style='display:flex;flex-direction:column;gap:3px'>{''.join(linhas)}</div>"

def render_overview_partida(partida, versao, mapa):
    """Tabela com todos os jogadores das duas equipes (semelhante ao op.gg)."""
    for tid, nome_time in ((100, "Time Azul"), (200, "Time Vermelho")):
        parts = [p for p in partida["participantes"] if p["team_id"] == tid]
        if not parts:
            continue
        venceu = parts[0]["win"]
        cor_res = "#2DD4A7" if venceu else "#E06B6B"
        st.markdown(
            f"<span style='color:{cor_res};font-weight:700'>"
            f"{'Vitória' if venceu else 'Derrota'}</span> "
            f"<span style='color:#A9BCCB'>— {nome_time}</span>",
            unsafe_allow_html=True,
        )
        total_dano = sum(p["dano"] for p in parts) or 1
        linhas = [{
            "Campeão": url_icone_campeao(p["champion_id"], versao, mapa),
            "Jogador": p["nick"],
            "Nv": p["nivel"],
            "KDA": f"{p['kills']}/{p['deaths']}/{p['assists']}",
            "Razão": f"{p['kda']}:1",
            "P/Kill": f"{p['kp']}%",
            "Dano": f"{p['dano']:,}".replace(",", "."),
            "Dano (% do time)": round(p["dano"] / total_dano * 100, 1),
            "CS": f"{p['cs']} ({p['cs_min']})",
            "Wards": p["wards"],
        } for p in parts]
        st.dataframe(
            pd.DataFrame(linhas), hide_index=True, width="stretch",
            column_config={
                "Campeão": st.column_config.ImageColumn("Campeão", width="small"),
                "Dano (% do time)": st.column_config.ProgressColumn(
                    "Dano (% do time)", format="%.0f%%", min_value=0, max_value=100,
                ),
            },
        )

def _fase_morte(t_s: int) -> str:
    """Fase do jogo de uma morte, pelo timestamp em segundos."""
    if t_s < 14 * 60:
        return "Início (0-14 min)"
    if t_s < 25 * 60:
        return "Meio (14-25 min)"
    return "Fim (25+ min)"


def _riot_client():
    return RiotClient(platform=st.session_state.get("platform", "br1"),
                      region=st.session_state.get("region", "americas"))


def _carregar_analise(partida, j):
    """(timeline, dados_normalizados) ou (None, None), com aviso na UI em falha.
    Timeline é buscada sob demanda e cacheada em disco (compartilhada pelos mapas)."""
    match_id = partida.get("match_id")
    if not match_id:
        st.caption("Partida sem identificador — não dá para reconstruir o mapa.")
        return None, None
    try:
        with st.spinner("Reconstruindo a partida a partir da timeline…"):
            timeline = analise_partidas.obter_timeline(_riot_client(), match_id)
            dados = analise_partidas.normalizar_timeline(timeline, j["puuid"])
        return timeline, dados
    except Exception as e:
        st.warning(f"Não foi possível carregar a timeline desta partida ({e}).")
        return None, None


def _render_mapa_mortes(partida, j, versao, mapa):
    """Fase 1: mapa de mortes do jogador sobre o minimapa, marcadores = ícone do
    campeão em preto e branco. Busca a timeline sob demanda (cacheada em disco)."""
    timeline, dados = _carregar_analise(partida, j)
    if dados is None:
        return
    match_id = partida["match_id"]

    mortes = [m for m in dados["mortes"] if m.get("x") is not None]
    if not mortes:
        st.caption("Sem mortes registradas nesta partida.")
        return

    resumo = {}
    for m in mortes:
        f = _fase_morte(m["t_s"])
        resumo[f] = resumo.get(f, 0) + 1

    fases = ["Todas"] + [f for f in ("Início (0-14 min)", "Meio (14-25 min)",
                                     "Fim (25+ min)") if f in resumo]
    fase = st.radio("Fase do jogo", fases, horizontal=True, key=f"fase_mortes_{match_id}")
    visiveis = (mortes if fase == "Todas"
                else [m for m in mortes if _fase_morte(m["t_s"]) == fase])

    icone_url = url_icone_campeao(j["champion_id"], versao, mapa)
    img, pontos = viz_partidas.mapa_e_pontos(visiveis, icone_url, versao)
    if img is None:
        st.warning("Não foi possível gerar o minimapa agora.")
        return
    w, h = img.size

    # participantId (1..10) -> participante, para o tooltip de quem matou.
    ordem_puuids = timeline.get("metadata", {}).get("participants", [])
    por_puuid = {p["puuid"]: p for p in partida["participantes"]}
    pid_para_part = {i: por_puuid.get(pu) for i, pu in enumerate(ordem_puuids, start=1)}

    xs, ys, textos = [], [], []
    for pt in pontos:
        m = pt["morte"]
        killer = pid_para_part.get(m.get("killer_id"))
        nome_k = killer["champion"] if killer else "execução (torre/minion)"
        n_assist = len(m.get("assist_ids") or [])
        partes = [
            f"<b>{m['t_s'] // 60}:{m['t_s'] % 60:02d}</b>",
            f"Morto por: {html.escape(nome_k)}",
            f"Assistências do inimigo: {n_assist}",
        ]
        # Fase 2: contexto da morte (isolamento, gank, déficit de ouro/nível).
        ctx = analise_partidas.contexto_morte(timeline, j["puuid"], m)
        nome_ctx = killer["champion"] if killer else None
        partes += [html.escape(s) for s in
                   analise_partidas.descrever_contexto_morte(ctx, nome_ctx)]
        xs.append(pt["px"])
        ys.append(pt["py"])
        textos.append("<br>".join(partes))

    # Imagem como fundo e camada de pontos transparentes só para o hover.
    fig = go.Figure()
    fig.add_layout_image(dict(source=img, xref="x", yref="y", x=0, y=0,
                              sizex=w, sizey=h, xanchor="left", yanchor="top",
                              sizing="stretch", layer="below"))
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers",
        marker=dict(size=30, color="rgba(0,0,0,0)"),
        hovertext=textos, hoverinfo="text",
        hoverlabel=dict(bgcolor="#0E1822", bordercolor="#C8AA6E",
                        font=dict(color="#E8EDF2", size=13)),
    ))
    fig.update_xaxes(visible=False, range=[0, w], constrain="domain")
    fig.update_yaxes(visible=False, range=[h, 0], scaleanchor="x", constrain="domain")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=460, showlegend=False,
                      dragmode=False, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width='stretch',
                    config={"displayModeBar": False},
                    key=f"mapa_mortes_{match_id}_{fase}")
    st.caption("Passe o mouse sobre um marcador para ver quem matou, assistências e o minuto.  "
               + " · ".join(f"{f}: {n}" for f, n in resumo.items()))


def _render_heatmap_posicao(partida, j, versao):
    """Fase 3: mapa de calor da posição do jogador (trajetória ~1/min) por fase,
    com a métrica de tempo no campo inimigo (proxy de overextend)."""
    timeline, dados = _carregar_analise(partida, j)
    if dados is None:
        return
    traj = [p for p in dados["trajetoria"] if p.get("x") is not None]
    if not traj:
        st.caption("Sem dados de posição nesta partida.")
        return

    fases_poss = ("Início (0-14 min)", "Meio (14-25 min)", "Fim (25+ min)")
    presentes = [f for f in fases_poss if any(_fase_morte(p["t_s"]) == f for p in traj)]
    fase = st.radio("Fase do jogo", ["Todas"] + presentes, horizontal=True,
                    key=f"fase_heat_{partida['match_id']}")
    vis = traj if fase == "Todas" else [p for p in traj if _fase_morte(p["t_s"]) == fase]

    base, pix = viz_partidas.base_e_pixels(vis, versao)
    if base is None:
        st.warning("Não foi possível gerar o minimapa agora.")
        return
    w, h = base.size

    fig = go.Figure()
    fig.add_layout_image(dict(source=base, xref="x", yref="y", x=0, y=0,
                              sizex=w, sizey=h, xanchor="left", yanchor="top",
                              sizing="stretch", layer="below"))
    fig.add_trace(go.Histogram2d(
        x=[p[0] for p in pix], y=[p[1] for p in pix],
        nbinsx=14, nbinsy=14, zsmooth="best", showscale=False, hoverinfo="skip",
        colorscale=[[0, "rgba(0,0,0,0)"], [0.2, "rgba(10,200,185,0.25)"],
                    [0.6, "rgba(240,200,80,0.55)"], [1, "rgba(224,107,107,0.9)"]],
    ))
    fig.update_xaxes(visible=False, range=[0, w], constrain="domain")
    fig.update_yaxes(visible=False, range=[h, 0], scaleanchor="x", constrain="domain")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=460, showlegend=False,
                      dragmode=False, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False},
                    key=f"heat_{partida['match_id']}_{fase}")

    mp = analise_partidas.metricas_posicionamento(vis, j["team_id"])
    if mp:
        st.caption(f"{mp['frames']} posições amostradas (~1/min) · "
                   f"{mp['pct_campo_inimigo']}% do tempo no campo inimigo.")


_OBJ_LABEL = {"DRAGON": "Dragão", "BARON_NASHOR": "Barão", "RIFTHERALD": "Arauto"}
_DRAGON_LABEL = {
    "FIRE_DRAGON": "Infernal", "WATER_DRAGON": "Oceano", "EARTH_DRAGON": "Montanha",
    "AIR_DRAGON": "Nuvem", "HEXTECH_DRAGON": "Hextech", "CHEMTECH_DRAGON": "Quimtech",
    "ELDER_DRAGON": "Ancião",
}


def _nome_objetivo(o: dict) -> str:
    nome = _OBJ_LABEL.get(o["tipo"], o["tipo"])
    if o["tipo"] == "DRAGON" and _DRAGON_LABEL.get(o.get("subtipo")):
        nome += f" ({_DRAGON_LABEL[o['subtipo']]})"
    return nome


def _render_timing_objetivos(partida, j, versao):
    """Fase 5: objetivos épicos (dragão/barão/arauto) no mapa, ligados à posição
    do jogador no momento — "onde você estava quando o objetivo caiu"."""
    timeline, dados = _carregar_analise(partida, j)
    if dados is None:
        return
    epicos = [o for o in dados["objetivos"]
              if o["tipo"] in ("DRAGON", "BARON_NASHOR", "RIFTHERALD")
              and o.get("x") is not None]
    if not epicos:
        st.caption("Nenhum objetivo épico (dragão/barão/arauto) registrado nesta partida.")
        return
    enr = analise_partidas.enriquecer_objetivos(timeline, j["puuid"], j["team_id"], epicos)

    base = viz_partidas.mapa_base(versao)
    if base is None:
        st.warning("Não foi possível gerar o minimapa agora.")
        return
    w, h = base.size

    obj_x, obj_y, obj_txt, obj_cor = [], [], [], []
    usr_x, usr_y, usr_txt, usr_cor, lin_x, lin_y = [], [], [], [], [], []
    for o in enr:
        nome = html.escape(_nome_objetivo(o))
        hora = f"{o['t_s'] // 60}:{o['t_s'] % 60:02d}"
        dist = o.get("dist_jogador")
        d_txt = f"{dist} de distância" if dist is not None else "posição desconhecida"
        cor = "#2DD4A7" if o["seu_time"] else "#E06B6B"  # verde = meu, vermelho = deles
        opx, opy = viz_partidas.coord_pixel(o["x"], o["y"], w, h)
        obj_x.append(opx)
        obj_y.append(opy)
        obj_cor.append(cor)
        obj_txt.append(
            f"<b>{nome}</b><br>{hora} · {'Seu time' if o['seu_time'] else 'Inimigo'}<br>"
            f"Você participou: {'sim' if o.get('participou') else 'não'} · {d_txt}"
        )
        if o.get("jogador_x") is not None:
            upx, upy = viz_partidas.coord_pixel(o["jogador_x"], o["jogador_y"], w, h)
            usr_x.append(upx)
            usr_y.append(upy)
            usr_cor.append(cor)  # ponto na cor do objetivo: verde = meu, vermelho = deles
            usr_txt.append(f"<b>Você</b> · {hora}<br>a {d_txt} do {nome}")
            lin_x += [opx, upx, None]
            lin_y += [opy, upy, None]

    fig = go.Figure()
    fig.add_layout_image(dict(source=base, xref="x", yref="y", x=0, y=0,
                              sizex=w, sizey=h, xanchor="left", yanchor="top",
                              sizing="stretch", layer="below"))
    _hover = dict(bgcolor="#0E1822", bordercolor="#C8AA6E",
                  font=dict(color="#E8EDF2", size=13))
    if lin_x:
        fig.add_trace(go.Scatter(x=lin_x, y=lin_y, mode="lines", hoverinfo="skip",
                                 line=dict(color="rgba(232,237,242,0.35)", width=1)))
    if usr_x:
        fig.add_trace(go.Scatter(
            x=usr_x, y=usr_y, mode="markers", hovertext=usr_txt, hoverinfo="text",
            hoverlabel=_hover,
            marker=dict(size=10, color=usr_cor, line=dict(color="#0E1822", width=1))))
    fig.add_trace(go.Scatter(
        x=obj_x, y=obj_y, mode="markers", hovertext=obj_txt, hoverinfo="text",
        marker=dict(size=18, color=obj_cor, symbol="diamond",
                    line=dict(color="#0E1822", width=1.5)),
        hoverlabel=_hover))
    fig.update_xaxes(visible=False, range=[0, w], constrain="domain")
    fig.update_yaxes(visible=False, range=[h, 0], scaleanchor="x", constrain="domain")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=460, showlegend=False,
                      dragmode=False, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False},
                    key=f"obj_{partida.get('match_id')}")

    seu = sum(1 for o in enr if o["seu_time"])
    part = sum(1 for o in enr if o["seu_time"] and o.get("participou"))
    st.caption(f"{len(enr)} objetivos épicos · seu time pegou {seu} (você participou de "
               f"{part}/{seu}). Verde = seu time, vermelho = inimigo (losango = objetivo, "
               "ponto = onde você estava). Passe o mouse em qualquer um.")


def _render_series_temporais(partida, j, versao):
    """Ferramenta 1: curva de vantagem de ouro/XP/CS do jogador vs. o oponente de
    lane ao longo do tempo, a partir dos participantFrames da timeline (cacheada)."""
    match_id = partida.get("match_id")
    if not match_id:
        st.caption("Partida sem identificador — não dá para reconstruir a evolução.")
        return
    try:
        with st.spinner("Reconstruindo a evolução a partir da timeline…"):
            timeline = analise_partidas.obter_timeline(_riot_client(), match_id)
            match = analise_partidas.obter_match(_riot_client(), match_id)
            st_ = analise_partidas.series_temporais(timeline, match, j["puuid"], j["team_id"])
    except Exception as e:
        st.warning(f"Não foi possível carregar a evolução desta partida ({e}).")
        return
    if not st_ or not st_.get("serie"):
        st.caption("Sem oponente de lane casado ou timeline insuficiente para a evolução.")
        return

    serie = st_["serie"]
    mins = [p["t_s"] / 60 for p in serie]
    # Ouro e XP estão na casa dos milhares; o CS, nas dezenas. No mesmo eixo o CS
    # ficaria colado no zero — então ele vai num eixo Y próprio (à direita), com os
    # dois eixos em faixas simétricas para o zero coincidir visualmente.
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color="rgba(169,188,203,.5)", width=1))
    fig.add_trace(go.Scatter(
        x=mins, y=[p["ouro_diff"] for p in serie], mode="lines", name="Ouro",
        line=dict(color="#E8C265", width=2),
        hovertemplate="%{x:.0f} min · Ouro: %{y:+.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=mins, y=[p["xp_diff"] for p in serie], mode="lines", name="XP",
        line=dict(color="#7FB3D5", width=2),
        hovertemplate="%{x:.0f} min · XP: %{y:+.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=mins, y=[p["cs_diff"] for p in serie], mode="lines", name="CS", yaxis="y2",
        line=dict(color="#2DD4A7", width=2),
        hovertemplate="%{x:.0f} min · CS: %{y:+.0f}<extra></extra>"))
    m1 = max(max(abs(p["ouro_diff"]) for p in serie),
             max(abs(p["xp_diff"]) for p in serie), 1)
    m2 = max(max(abs(p["cs_diff"]) for p in serie), 1)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#A9BCCB"),
                      legend=dict(orientation="h", y=1.12, x=0),
                      xaxis=dict(title="minuto", gridcolor="rgba(255,255,255,.06)"),
                      yaxis=dict(title="ouro / xp (você − oponente)",
                                 range=[-m1 * 1.1, m1 * 1.1],
                                 gridcolor="rgba(255,255,255,.06)", zeroline=False),
                      yaxis2=dict(title="CS (você − oponente)",
                                  range=[-m2 * 1.1, m2 * 1.1],
                                  overlaying="y", side="right", showgrid=False,
                                  zeroline=False))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                    key=f"series_{match_id}")
    m = st_.get("marcos", {})
    def _delta(k):
        d = m.get(k, {})
        return (f"@{k}: ouro {d.get('ouro', 0):+}, xp {d.get('xp', 0):+}, cs {d.get('cs', 0):+}"
                if d else "")
    partes = [s for s in (_delta("10"), _delta("14")) if s]
    alvo = "oponentes de lane" if st_.get("n_oponentes", 1) > 1 else "oponente de lane"
    st.caption(f"Vantagem acumulada contra o {alvo}. Acima de 0 = você na frente.  "
               + " · ".join(partes))


# Métricas que a Riot devolve como FRAÇÃO 0-1 (challenges): exibir como porcentagem —
# "0.2" no card parece 0.2% quando na verdade é 20% (mesma escala dos benchmarks).
_METRICAS_FRACAO = {"pct_dano_time", "kpa"}


def _fmt_valor_metrica(metrica: str, valor):
    """Valor de métrica para exibição: frações 0-1 viram '20%'; o resto passa direto."""
    if metrica in _METRICAS_FRACAO and isinstance(valor, (int, float)):
        return f"{valor * 100:.0f}%"
    return valor


_GRUPOS_STATS = [
    ("Combate", "combate", [
        ("dano_campeoes", "Dano a campeões"), ("dano_fisico", "Dano físico"),
        ("dano_magico", "Dano mágico"), ("dano_verdadeiro", "Dano verdadeiro"),
        ("dano_por_min", "Dano / min"), ("pct_dano_time", "% dano do time"),
        ("dano_recebido", "Dano recebido"), ("dano_mitigado", "Dano mitigado"),
        ("cura_aliados", "Cura em aliados"), ("escudo_aliados", "Escudo em aliados"),
        ("tempo_cc_aplicado_s", "Tempo de CC (s)"), ("solo_kills", "Solo kills")]),
    ("Visão", "visao", [
        ("vision_score", "Vision score"), ("vision_min", "Visão / min"),
        ("control_wards", "Control wards"), ("ward_takedowns", "Wards destruídas"),
        ("vantagem_visao_oponente", "Vantagem de visão")]),
    ("Economia / Lane", "economia", [
        ("ouro_min", "Ouro / min"), ("cs_min", "CS / min"),
        ("cs_rota_10m", "CS de rota (10m)"), ("cs_jungle_10m", "CS de selva (10m)"),
        ("vantagem_cs_max_oponente", "Maior vantagem de CS")]),
    ("Sobrevivência", "sobrevivencia", [
        ("tempo_morto_s", "Tempo morto (s)"), ("maior_tempo_vivo_s", "Maior tempo vivo (s)"),
        ("sobreviveu_hp_critico", "Sobreviveu com HP crítico")]),
    ("Habilidade", "habilidade", [
        ("skillshots_acertados", "Skillshots acertados"),
        ("skillshots_desviados", "Skillshots desviados"),
        ("abates_em_desvantagem", "Abates em desvantagem")]),
]


def _render_stats_ricas(partida, j):
    """Ferramenta 2: painel das estatísticas ricas (challenges & cia.) que já são
    extraídas mas nunca aparecem na aba — agrupadas por tema, mais os pings."""
    match_id = partida.get("match_id")
    if not match_id:
        st.caption("Partida sem identificador — sem estatísticas detalhadas.")
        return
    try:
        match = analise_partidas.obter_match(_riot_client(), match_id)
        ricos = analise_partidas.extrair_dados_ricos(match, j["puuid"])
    except Exception as e:
        st.warning(f"Não foi possível carregar as estatísticas ({e}).")
        return
    if not ricos:
        st.caption("Sem estatísticas detalhadas para esta partida.")
        return

    def _fmt(v):
        if isinstance(v, float):
            return f"{v:.2f}" if abs(v) < 10 else f"{v:,.0f}".replace(",", ".")
        if isinstance(v, int):
            return f"{v:,}".replace(",", ".")
        return v

    # Cada grupo vira uma tabela compacta (Métrica/Valor), duas por linha.
    tabelas = []
    for titulo, secao, campos in _GRUPOS_STATS:
        bloco = ricos.get(secao, {}) or {}
        linhas = [{"Métrica": rotulo,
                   "Valor": (_fmt_valor_metrica(k, bloco[k]) if k in _METRICAS_FRACAO
                             else _fmt(bloco[k]))}
                  for k, rotulo in campos if k in bloco]
        if linhas:
            tabelas.append((titulo, linhas))

    pings = ricos.get("comportamento_pings", {}) or {}
    ativos = {k: v for k, v in pings.items() if v}
    if ativos:
        rotulos = {"allInPings": "All-in", "assistMePings": "Ajuda", "basicPings": "Básico",
                   "commandPings": "Comando", "dangerPings": "Perigo",
                   "enemyMissingPings": "Inimigo sumido", "enemyVisionPings": "Visão inimiga",
                   "getBackPings": "Recuar", "holdPings": "Segurar",
                   "needVisionPings": "Preciso de visão", "onMyWayPings": "A caminho",
                   "pushPings": "Pushar", "retreatPings": "Retirada",
                   "visionClearedPings": "Visão limpa"}
        tabelas.append(("Comunicação (pings)", [
            {"Métrica": rotulos.get(k, k), "Valor": v}
            for k, v in sorted(ativos.items(), key=lambda kv: -kv[1])]))

    if not tabelas:
        st.caption("Sem estatísticas detalhadas para esta partida.")
        return
    for i in range(0, len(tabelas), 2):
        cols = st.columns(2)
        for col, (titulo, linhas) in zip(cols, tabelas[i:i + 2]):
            with col:
                st.markdown(f"**{titulo}**")
                st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")


def _render_build(partida, j, versao):
    """Ferramenta 3: linha do tempo das compras de itens e a ordem de habilidades,
    a partir dos eventos da timeline (hoje ignorados)."""
    match_id = partida.get("match_id")
    if not match_id:
        st.caption("Partida sem identificador — sem build.")
        return
    try:
        timeline = analise_partidas.obter_timeline(_riot_client(), match_id)
        b = analise_partidas.linha_do_tempo_build(timeline, j["puuid"])
    except Exception as e:
        st.warning(f"Não foi possível carregar a build ({e}).")
        return
    # Esconde peças de receita (componentes que constroem em outro item), preservando:
    # botas (tag Boots), itens de lane (tag Lane — ampla de propósito, inclui Espada
    # Longa, Doran e Lacre Sombrio), a Lágrima ("gota"), o Fulgor e o Capítulo Perdido.
    meta_itens = obter_meta_itens(versao)

    def _mostrar(item_id) -> bool:
        meta = meta_itens.get(str(item_id))
        if not meta or not meta["componente"]:
            return True  # sem metadado, item finalizado ou consumível → mostra
        tags = meta["tags"]
        nome = meta["nome"].lower()
        return ("Boots" in tags or "Lane" in tags
                or "lágrima" in nome or "fulgor" in nome or "capítulo" in nome)

    compras = [i for i in b.get("itens", [])
               if i["acao"] != "venda" and i["item_id"] and _mostrar(i["item_id"])]
    if not compras:
        st.caption("Sem eventos de compra registrados nesta partida.")
        return

    st.markdown("**Ordem de compra**")
    linha = []
    for it in compras:
        op = "0.6" if it["acao"] == "desfeita" else "1"
        risca = "filter:grayscale(1);" if it["acao"] == "desfeita" else ""
        meta = meta_itens.get(str(it["item_id"]), {})
        nome = meta.get("nome") or f"Item {it['item_id']}"
        ouro = meta.get("ouro")
        titulo = f"{nome} · {ouro} de ouro" if ouro else nome
        if it["acao"] == "desfeita":
            titulo += " (compra desfeita)"
        linha.append(
            f"<div style='display:inline-flex;flex-direction:column;align-items:center;"
            f"margin:0 6px 8px 0;opacity:{op}'>"
            f"<img src='{url_item(it['item_id'], versao)}' width='34' height='34' "
            f"title='{html.escape(titulo)}' "
            f"style='border-radius:6px;border:1px solid var(--border);{risca}'>"
            f"<span style='color:var(--muted);font-size:.66rem;margin-top:2px'>"
            f"{it['t_s'] // 60}:{it['t_s'] % 60:02d}</span></div>")
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;align-items:flex-start'>"
                f"{''.join(linha)}</div>", unsafe_allow_html=True)
    st.caption("Itens em ordem de compra (minuto embaixo). Cinza/translúcido = compra desfeita.")

    skills = b.get("skills", [])
    if skills:
        seq = " → ".join(analise_partidas._SLOT_LABEL[s["slot"]] for s in skills)
        st.markdown("**Ordem de habilidades**")
        st.markdown(f"<div style='color:var(--text);font-size:.95rem;letter-spacing:1px'>"
                    f"{seq}</div>", unsafe_allow_html=True)
        if b.get("ordem_max"):
            st.caption(f"Ordem de maximização: {b['ordem_max']}")


def _render_analise_ia(partida, j):
    """Análise textual da partida pelo Tutor (one-shot), sob demanda. Cruza as
    estatísticas ricas com a timeline e descreve fortes/fracos/mortes/erros."""
    chave = partida.get("match_id") or partida.get("fim_ts")
    ss_key = f"_analise_ia_{chave}"
    if ss_key not in st.session_state:
        st.caption("O Tutor analisa pontos fortes, fracos, momentos de morte, erros "
                   "repetidos e bons lances desta partida.")
        if not st.button("Gerar análise da partida", key=f"btn_ia_{chave}"):
            return
        if not partida.get("match_id"):
            st.warning("Partida sem identificador — não dá para analisar.")
            return
        try:
            with st.spinner("O Tutor está analisando a partida…"):
                dossie = analise_partidas.dossie_partida(
                    _riot_client(), partida["match_id"], j["puuid"], j["team_id"])
                st.session_state[ss_key] = analisar_partida_texto(
                    dossie, nick=j.get("nick", ""), campeao=j.get("champion", ""),
                    rota=ROLE_LABELS.get(j.get("lane", ""), j.get("lane", "")),
                    resultado="Vitória" if partida["venceu"] else "Derrota")
        except Exception as e:
            st.warning(f"Não foi possível gerar a análise ({e}).")
            return
    st.markdown(st.session_state[ss_key])
    if st.button("Refazer análise", key=f"btn_ia_redo_{chave}"):
        del st.session_state[ss_key]
        st.rerun()


def render_card_partida(partida, versao, mapa, fila_label=None):
    j = partida["jogador"]
    if not j:
        return
    venceu = partida["venceu"]
    cor = "#2DD4A7" if venceu else "#E06B6B"
    tint = "rgba(45,212,167,.10)" if venceu else "rgba(224,107,107,.10)"
    resultado = "Vitória" if venceu else "Derrota"
    dur = partida["duracao_seg"]
    lane = ROLE_LABELS.get(j["lane"], j["lane"] or "—")
    # Selo da fila: reforça que a lista mostra só partidas da fila selecionada.
    fila_badge = (
        f"<span style='display:inline-block;margin-top:4px;padding:1px 8px;border-radius:8px;"
        f"background:rgba(232,194,101,.12);border:1px solid var(--border);"
        f"color:var(--gold);font-size:.68rem;font-weight:600'>{html.escape(fila_label)}</span>"
        if fila_label else ""
    )

    times = {100: [], 200: []}
    for p in partida["participantes"]:
        times.setdefault(p["team_id"], []).append(p)

    # KDA com cor por faixa de desempenho
    try:
        kda_val = float(j["kda"])
    except (TypeError, ValueError):
        kda_val = 0.0
    kda_cor = ("#E8C265" if kda_val >= 4 else "#2DD4A7" if kda_val >= 3
               else "#7FB3D5" if kda_val >= 2 else "#A9BCCB")

    champ_url = url_icone_campeao(j["champion_id"], versao, mapa)
    itens = [it for it in j["itens"] if it]
    itens_html = "".join(_img_tag(url_item(it, versao), 24) for it in itens)
    itens_block = (f"<div style='display:flex;gap:3px;margin-top:7px;flex-wrap:wrap'>{itens_html}</div>"
                   if itens else "")

    card = (
        f"<div style='display:flex;flex-wrap:wrap;align-items:center;gap:18px;"
        f"padding:14px 18px;margin-bottom:10px;border:1px solid var(--border);"
        f"border-left:4px solid {cor};border-radius:12px;"
        f"background:linear-gradient(90deg,{tint},rgba(14,24,34,.35))'>"

        # Resultado / rota / tempo / fila
        f"<div style='min-width:92px'>"
        f"<div style='color:{cor};font-weight:700;font-size:1.05rem'>{resultado}</div>"
        f"<div style='color:var(--muted);font-size:.78rem;margin-top:2px'>{html.escape(lane)}</div>"
        f"<div style='color:var(--muted);font-size:.74rem'>{dur // 60}m {dur % 60:02d}s · {tempo_atras(partida['fim_ts'])}</div>"
        f"{fila_badge}"
        f"</div>"

        # Ícone do campeão + nível
        f"<div style='position:relative;width:52px;height:52px;flex:none'>"
        f"<img src='{champ_url}' width='52' height='52' "
        f"style='border-radius:50%;border:2px solid {cor};object-fit:cover'>"
        f"<span style='position:absolute;bottom:-5px;left:50%;transform:translateX(-50%);"
        f"background:var(--bg-0);border:1px solid var(--border);border-radius:8px;"
        f"font-size:.62rem;padding:0 6px;color:var(--gold)'>{j['nivel']}</span>"
        f"</div>"

        # KDA + métricas + itens
        f"<div style='flex:1;min-width:170px'>"
        f"<div style='font-size:1.15rem;font-weight:700;color:var(--text)'>"
        f"{j['kills']} <span style='color:var(--muted)'>/</span> "
        f"<span style='color:#E06B6B'>{j['deaths']}</span> "
        f"<span style='color:var(--muted)'>/</span> {j['assists']}</div>"
        f"<div style='color:{kda_cor};font-size:.85rem;font-weight:600'>{j['kda']}:1 KDA</div>"
        f"<div style='color:var(--muted);font-size:.76rem;margin-top:1px'>"
        f"CS {j['cs']} ({j['cs_min']}/min) · P/Kill {j['kp']}%</div>"
        f"{itens_block}"
        f"</div>"

        # Rosters dos dois times
        f"<div style='display:flex;gap:16px'>"
        f"{_roster_html(times.get(100, []), versao, mapa, j['puuid'])}"
        f"{_roster_html(times.get(200, []), versao, mapa, j['puuid'])}"
        f"</div>"

        f"</div>"
    )
    st.markdown(card, unsafe_allow_html=True)

    # Dropdown único por partida: escolhe qual visão analisar (nada é renderizado
    # — nem chamada de rede — até o usuário selecionar uma opção).
    chave = partida.get("match_id") or partida.get("fim_ts")
    opcoes = ["Selecione uma análise", "Análise do Tutor", "Detalhes da partida",
              "Estatísticas detalhadas", "Evolução (ouro/XP/CS)", "Build & habilidades",
              "Mapa de mortes", "Mapa de calor (posicionamento)",
              "Timing de objetivos"]
    escolha = st.selectbox("Análise da partida", opcoes,
                           key=f"analise_{chave}", label_visibility="collapsed")
    if escolha == "Análise do Tutor":
        _render_analise_ia(partida, j)
    elif escolha == "Detalhes da partida":
        render_overview_partida(partida, versao, mapa)
    elif escolha == "Estatísticas detalhadas":
        _render_stats_ricas(partida, j)
    elif escolha == "Evolução (ouro/XP/CS)":
        _render_series_temporais(partida, j, versao)
    elif escolha == "Build & habilidades":
        _render_build(partida, j, versao)
    elif escolha == "Mapa de mortes":
        _render_mapa_mortes(partida, j, versao, mapa)
    elif escolha == "Mapa de calor (posicionamento)":
        _render_heatmap_posicao(partida, j, versao)
    elif escolha == "Timing de objetivos":
        _render_timing_objetivos(partida, j, versao)

def _render_padroes_recentes(historico, versao):
    """Fase 6: visão geral dos padrões nas últimas partidas (clusters de morte,
    contexto, objetivos, exposição) + análise escrita do Tutor + mapa de calor."""
    with st.expander("Padrões nas últimas partidas (visão geral)"):
        n = min(5, len(historico))
        if st.button(f"Analisar padrões das últimas {n} partidas", key="btn_padroes"):
            j0 = historico[0].get("jogador") or {}
            with st.spinner("Analisando as timelines e gerando a análise do Tutor…"):
                resumo = analise_partidas.resumo_padroes(
                    _riot_client(), historico, j0.get("puuid"), j0.get("team_id"), n)
                st.session_state["_padroes"] = resumo
                # Análise escrita do Tutor (base de conhecimento) já junto do botão.
                try:
                    insights = analise_partidas.descrever_padroes(resumo)
                    st.session_state["_analise_padroes_txt"] = analisar_padroes_texto(
                        resumo, insights, nick=j0.get("nick", ""),
                        rota=ROLE_LABELS.get(j0.get("lane", ""), j0.get("lane", "")))
                except Exception as e:
                    st.session_state["_analise_padroes_txt"] = (
                        f"Não foi possível gerar a análise do Tutor ({e}).")
        resumo = st.session_state.get("_padroes")
        if not resumo:
            st.caption("É o mesmo dado que o tutor usa para falar de posicionamento e mortes.")
            return
        for linha in analise_partidas.descrever_padroes(resumo):
            st.markdown(f"- {linha}")

        # Análise escrita do Tutor sobre o padrão (gerada junto com o botão acima).
        txt = st.session_state.get("_analise_padroes_txt")
        if txt:
            st.markdown(txt)

        pontos = resumo.get("mortes_pontos", [])
        base, pix = viz_partidas.base_e_pixels(pontos, versao)
        if base is None or not pix:
            return
        w, h = base.size
        fig = go.Figure()
        fig.add_layout_image(dict(source=base, xref="x", yref="y", x=0, y=0,
                                  sizex=w, sizey=h, xanchor="left", yanchor="top",
                                  sizing="stretch", layer="below"))
        fig.add_trace(go.Histogram2d(
            x=[p[0] for p in pix], y=[p[1] for p in pix], nbinsx=16, nbinsy=16,
            zsmooth="best", showscale=False, hoverinfo="skip",
            colorscale=[[0, "rgba(0,0,0,0)"], [0.3, "rgba(240,200,80,0.45)"],
                        [1, "rgba(224,107,107,0.9)"]]))
        fig.update_xaxes(visible=False, range=[0, w], constrain="domain")
        fig.update_yaxes(visible=False, range=[h, 0], scaleanchor="x", constrain="domain")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=460, showlegend=False,
                          dragmode=False, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False},
                        key="heat_mortes_geral")
        st.caption("Mapa de calor das suas mortes nessas partidas.")


def render_historico(historico):
    fila_label = FILAS.get(_fila_atual(), {}).get("label", "")
    if not historico:
        st.info(f"Nenhuma partida de **{fila_label}** encontrada para exibir. "
                "Troque a fila na barra lateral para ver outras.")
        return
    versao = obter_versao_mais_recente()
    mapa = obter_mapa_campeoes(versao)
    st.caption(f"Últimas {len(historico)} partidas de {fila_label} "
               "(a análise mostra apenas partidas da fila selecionada na barra lateral).")
    _render_padroes_recentes(historico, versao)
    for partida in historico:
        render_card_partida(partida, versao, mapa, fila_label)

def _fila_atual() -> str:
    """Fila ativa da página do jogador (solo/flex/normal). Define a queue das partidas,
    os benchmarks comparados e o slot de persistência (plano/conversa por rota+fila)."""
    return st.session_state.get("fila_atual") or FILA_PADRAO


def _thread_id() -> str:
    """Thread de memória do agente = usuário + jogador + conversa ativa: trocar de login,
    de conversa salva OU de fila (a conversa ativa é por rota+fila) isola a memória."""
    jogador = f"{st.session_state.game_name}#{st.session_state.tag_line}".strip().lower()
    return f"u{st.session_state.user_id}:{jogador}:c{st.session_state.get('conversa_id') or 0}"


@st.fragment
def render_mentoria(tutor_grafo, prompt_sistema, player_profile, thread_id):
    """Fragment: cada troca de mensagens reroda SÓ o chat. O rerun no fim de cada
    resposta dobra a troca nova para CIMA da caixa de digitação — o st.chat_input
    dentro de abas é inline (não fixa no rodapé da janela), então sem isso a resposta
    ficava pendurada ABAIXO da caixa até a interação seguinte (feedback de usuário)."""
    st.markdown("---")

    # Auto-cura: se a conversa sumiu da memória mas existe no disco, recarrega ANTES de
    # exibir/regenerar — evita mostrar a tela vazia e evita regenerar a saudação por cima
    # de um histórico salvo (causa do "a conversa aparece vazia").
    if not st.session_state.mensagens_chat:
        salva = carregar_sessao(st.session_state.user_id,
                                st.session_state.game_name, st.session_state.tag_line,
                                rota=st.session_state.get("posicao_atual"), fila=_fila_atual())
        st.session_state.conversa_id = salva.get("conversa_id")
        if salva.get("mensagens"):
            st.session_state.mensagens_chat = salva["mensagens"]
            st.session_state.tutoria_encerrada = salva.get("tutoria_encerrada", False)
            semear_memoria(tutor_grafo, prompt_sistema, salva["mensagens"], thread_id)

    # Renderiza mensagens antigas
    for msg in st.session_state.mensagens_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Gatilho Inicial Oculto (Proatividade do Agente)
    if len(st.session_state.mensagens_chat) == 0:
        mensagem_gatilho = "Olá tutor, use sua ferramenta analisar_jogador para obter meus dados, aponte meu principal problema e me faça a primeira pergunta socrática para começarmos."

        with st.chat_message("assistant"):
            with _carregando(f"Analisando métricas de {nome_exibicao(player_profile['nick'])}"):
                # O agente busca os dados (analisar_jogador) e responde; injeta o
                # prompt de sistema como mensagem zero. Reflexão/auto-crítica embutida.
                texto_resposta = responder_tutor(
                    tutor_grafo, [("user", mensagem_gatilho)], thread_id,
                    modo="socratico", system=prompt_sistema,
                )
                st.write(texto_resposta)

        st.session_state.mensagens_chat.append({"role": "assistant", "content": texto_resposta})
        # Salva só a conversa (o plano é escrito por _persistir_plano; não mexemos nele aqui).
        salvar_sessao(st.session_state.user_id,
                      st.session_state.game_name, st.session_state.tag_line,
                      mensagens=st.session_state.mensagens_chat,
                      tutoria_encerrada=st.session_state.tutoria_encerrada,
                      rota=st.session_state.get("posicao_atual"), fila=_fila_atual(),
                      conversa_id=st.session_state.get("conversa_id"))

    # Resposta pendente: a pergunta já está no histórico (renderizado acima); a resposta
    # é gerada AQUI, entre o histórico e a caixa — spinner e texto nascem no lugar
    # definitivo, sem reordenar nada depois (a caixa nunca "pula").
    if entrada_usuario := st.session_state.pop("chat_pendente", None):
        with st.chat_message("assistant"):
            with _carregando("Pensando"):

                # Fluxo de Desistência/Impaciência: o tutor PARA de perguntar e responde
                # direto (explicação tática + motivação), mas a tutoria NÃO encerra.
                if usuario_desistiu(entrada_usuario):
                    modo = "resposta_direta"
                    input_modificado = (
                        f"Usuário disse: '{entrada_usuario}'\n\n"
                        "[COMANDO INTERNO DO SISTEMA: O usuário pediu uma resposta direta / demonstrou "
                        "impaciência ou desânimo. PARE o método socrático nesta resposta. "
                        "Forneça uma explicação tática direta e prática sobre a métrica deficitária, "
                        "diga o que fazer no jogo e inclua uma frase curta de motivação. "
                        "NÃO faça NENHUMA pergunta. NÃO encerre a conversa nem escreva tags de encerramento.]"
                    )
                    texto_resposta = responder_tutor(
                        tutor_grafo, [("user", input_modificado)], thread_id, modo=modo
                    )

                # Fluxo de Pergunta Factual (o jogador perguntou algo sobre os dados dele):
                # responde direto com as ferramentas, sem devolver pergunta socrática.
                elif pergunta_factual(entrada_usuario):
                    modo = "resposta_direta"
                    input_modificado = (
                        f"{entrada_usuario}\n\n"
                        "[COMANDO INTERNO DO SISTEMA: O jogador fez uma PERGUNTA factual sobre os dados dele. "
                        "Responda-a DIRETAMENTE usando as ferramentas (detalhar_partida/analisar_jogador/comparar_com_elo). "
                        "NÃO faça NENHUMA pergunta socrática nesta resposta.]"
                    )
                    texto_resposta = responder_tutor(
                        tutor_grafo, [("user", input_modificado)], thread_id, modo=modo
                    )

                # Fluxo Normal (Socrático) — com FIM DE CICLO (feedback de usuário +
                # teoria: o método socrático converge para uma síntese, e o suporte
                # deve diminuir quando o aprendiz demonstra competência). O prompt
                # manda o tutor fechar sozinho quando o jogador verbaliza a conclusão;
                # este contador é o guard rail para quando o modelo não percebe.
                else:
                    trocas = st.session_state.get("trocas_ciclo_socratico", 0) + 1
                    st.session_state.trocas_ciclo_socratico = trocas
                    if trocas >= 4:
                        input_modificado = (
                            f"{entrada_usuario}\n\n"
                            "[COMANDO INTERNO DO SISTEMA: este ciclo socrático já tem várias trocas. "
                            "FECHE o ciclo NESTA resposta (Fechamento de Ciclo da REGRA 2): sintetize "
                            "em 2-3 linhas o que o jogador concluiu até aqui e a ação prática no jogo, "
                            "NÃO faça NENHUMA pergunta e termine devolvendo a escolha do próximo passo "
                            "como AFIRMAÇÃO sem '?' (outra dúvida, analisar uma partida ou o plano de treino).]"
                        )
                        texto_resposta = responder_tutor(
                            tutor_grafo, [("user", input_modificado)], thread_id,
                            modo="resposta_direta",
                        )
                    else:
                        texto_resposta = responder_tutor(
                            tutor_grafo, [("user", entrada_usuario)], thread_id, modo="socratico"
                        )

                # A tutoria NUNCA encerra. Se o modelo ainda inventar uma tag de
                # encerramento (ex.: diante de desabafos como "sou ruim"), ela é apenas
                # removida da exibição — jamais trava o chat.
                texto_limpo = texto_resposta.replace("[FIM_TUTORIA]", "").strip()
                # Resposta sem pergunta = ciclo fechado (síntese, resposta direta ou
                # desistência): zera o contador — o próximo tema começa um ciclo novo.
                if "?" not in texto_limpo:
                    st.session_state.trocas_ciclo_socratico = 0
                st.write(texto_limpo)

        st.session_state.mensagens_chat.append({"role": "assistant", "content": texto_limpo})
        salvar_sessao(st.session_state.user_id,
                      st.session_state.game_name, st.session_state.tag_line,
                      mensagens=st.session_state.mensagens_chat,
                      tutoria_encerrada=st.session_state.tutoria_encerrada,
                      rota=st.session_state.get("posicao_atual"), fila=_fila_atual(),
                      conversa_id=st.session_state.get("conversa_id"))

    # Caixa de digitação — SEMPRE o último elemento do chat. O envio só registra a
    # pergunta e reroda o fragmento (instantâneo): o próximo ciclo mostra a pergunta
    # no histórico e gera a resposta acima da caixa, já na posição definitiva.
    if entrada := st.chat_input("Você:"):
        st.session_state.mensagens_chat.append({"role": "user", "content": entrada})
        st.session_state.chat_pendente = entrada
        _rerun_fragmento()

def _historico_planos() -> list:
    """Lista (mutável no session_state) dos planos anteriores desta rota — restauráveis."""
    return st.session_state.setdefault("historico_planos", [])


def _arquivar_plano(plano) -> None:
    """Guarda um plano no histórico (no topo), sem duplicar a mesma identidade. Limita o
    tamanho para o JSON não crescer sem fim."""
    if not plano:
        return
    hist = _historico_planos()
    assin = assinatura_plano(plano)
    hist[:] = [p for p in hist if assinatura_plano(p) != assin]
    hist.insert(0, plano)
    del hist[12:]


def _persistir_plano(plano, tutor_grafo, thread_id):
    """Espelha o plano no holder, no State do grafo e na memória de longo prazo."""
    st.session_state.caixa_plano["plano"] = plano
    st.session_state.plano = plano
    semear_plano(tutor_grafo, plano, thread_id)
    # Salva o plano, o histórico de planos e as métricas já dominadas (NÃO mexe na conversa —
    # o monitor autônomo chama isto a cada 180s e não pode sobrescrever/encolher o chat).
    salvar_sessao(st.session_state.user_id,
                  st.session_state.game_name, st.session_state.tag_line,
                  rota=st.session_state.get("posicao_atual"), fila=_fila_atual(), plano=plano,
                  metricas_superadas=st.session_state.get("metricas_superadas", {}),
                  historico_planos=_historico_planos())


def _restaurar_plano(plano_escolhido, tutor_grafo, thread_id):
    """Volta a um plano anterior com todo o seu histórico de evolução. Arquiva o plano ativo
    (para não perdê-lo) e tira o escolhido do histórico antes de ativá-lo."""
    _arquivar_plano(st.session_state.get("plano"))
    assin = assinatura_plano(plano_escolhido)
    hist = _historico_planos()
    hist[:] = [p for p in hist if assinatura_plano(p) != assin]
    _persistir_plano(plano_escolhido, tutor_grafo, thread_id)


def _apagar_do_historico(plano_escolhido):
    """Remove de vez um plano salvo dos 'Planos anteriores' (não mexe no plano ativo)."""
    assin = assinatura_plano(plano_escolhido)
    hist = _historico_planos()
    hist[:] = [p for p in hist if assinatura_plano(p) != assin]
    salvar_sessao(st.session_state.user_id,
                  st.session_state.game_name, st.session_state.tag_line,
                  rota=st.session_state.get("posicao_atual"), fila=_fila_atual(),
                  historico_planos=hist)


def _fim_ts_mais_recente():
    """Timestamp da partida mais recente do jogador (marco do baseline do passo 5)."""
    dados = obter_dados_jogador(
        st.session_state.game_name, st.session_state.tag_line,
        st.session_state.get("platform", "br1"), st.session_state.get("region", "americas"),
        _fila_atual(),
    )
    hist = dados.get("historico") or []
    return hist[0]["fim_ts"] if hist else None


def _metricas_superadas_rota(rota: str) -> list[str]:
    """Lista (mutável no session_state) das métricas já dominadas nesta rota+fila.
    A chave inclui a fila (`solo:MIDDLE`); chaves antigas sem ':' eram solo."""
    mapa = st.session_state.setdefault("metricas_superadas", {})
    return mapa.setdefault(f"{_fila_atual()}:{rota}", [])


def _criar_plano(player_profile, tutor_grafo, thread_id):
    """Gera e persiste um plano novo, marcando o baseline de partidas (passo 5).
    Ataca a próxima métrica mais fraca AINDA não dominada: quando a meta de uma métrica é
    atingida e o jogador gera um novo plano, ela é marcada como superada e o foco avança.
    Usa a MESMA base de comparação do diagnóstico (mono/pool/rota) para definir o alvo."""
    benchmarks = player_profile.get("benchmarks_base") or _benchmarks_rota_cached(
        player_profile["posicao"], player_profile.get("regiao"), _fila_atual())
    rota = player_profile["posicao"]
    superadas = _metricas_superadas_rota(rota)

    plano_atual = st.session_state.get("plano")
    if plano_atual:
        # Gerar um novo plano AVANÇA para a próxima métrica mais fraca (não repete a atual).
        atualizar_valor_atual(plano_atual, player_profile)
        if meta_atingida(plano_atual) and plano_atual["metrica"] not in superadas:
            superadas.append(plano_atual["metrica"])  # meta batida → métrica dominada
        metrica_alvo = avancar_metrica(player_profile, plano_atual["metrica"], superadas)
    else:
        # Primeiro plano da rota: ataca a métrica mais fraca ainda não dominada.
        metrica_alvo = proxima_metrica(player_profile, superadas)

    # Caso o ciclo volte para a mesma métrica (rota com 1 métrica), evita repetir os drills.
    evitar = None
    if plano_atual and plano_atual.get("metrica") == metrica_alvo:
        evitar = [p["descricao"] for p in plano_atual.get("passos", [])]

    novo = gerar_plano_treino(player_profile, benchmarks, _fim_ts_mais_recente(),
                              evitar_metas=evitar, metrica_alvo=metrica_alvo)
    # Guarda o plano anterior no histórico (restaurável) antes de trocar pelo novo.
    _arquivar_plano(plano_atual)
    _persistir_plano(novo, tutor_grafo, thread_id)


# Passo 6: reavaliação autônoma — sem botão. O monitor detecta novas partidas e
# atualiza o progresso sozinho, limitado a uma chamada à Riot a cada INTERVALO.
INTERVALO_VERIFICACAO = timedelta(minutes=10)


def verificar_partidas_automaticamente(plano: dict) -> str:
    """Detecta partidas novas e reavalia o plano sem intervenção do usuário. Muta o plano
    (bookkeeping/medições) e retorna o status:
    'throttled' (dentro da janela, sem rede) | 'baseline' (definiu o marco) |
    'reavaliou' (registrou nova medição) | 'sem_novidade'."""
    agora = datetime.now()
    ultima = plano.get("ultima_verificacao")
    if ultima:
        try:
            if agora - datetime.fromisoformat(ultima) < INTERVALO_VERIFICACAO:
                return "throttled"
        except ValueError:
            pass

    platform = st.session_state.get("platform", "br1")
    region = st.session_state.get("region", "americas")
    fila = _fila_atual()

    # Checagem BARATA primeiro (1 chamada à Riot): se a partida mais recente é a mesma
    # da última verificação, não invalida o cache nem recoleta as ~40 partidas — o caso
    # comum a cada janela, que antes congelava a interação do usuário por segundos.
    # (Caches/planos antigos sem puuid/ultimo_match_id_visto caem no caminho completo
    # uma vez e passam a ter os campos.)
    ultimo_visto = plano.get("ultimo_match_id_visto")
    if ultimo_visto:
        try:
            puuid = obter_dados_jogador(st.session_state.game_name, st.session_state.tag_line,
                                        platform, region, fila).get("puuid")
            if puuid:
                # Checa a MESMA fila do plano (queue própria), não sempre a solo.
                ids = RiotClient(platform=platform, region=region).get_match_ids(
                    puuid, count=1, queue=FILAS[fila]["queue"])
                if ids and ids[0] == ultimo_visto:
                    plano["ultima_verificacao"] = agora.isoformat()
                    return "sem_novidade"
        except Exception:
            pass  # checagem barata indisponível → segue o caminho completo

    invalidar_cache_jogador()  # força o re-fetch das partidas mais recentes
    perfil, _ = buscar_perfil_e_formatar(
        st.session_state.game_name, st.session_state.tag_line, plano["posicao"],
        platform=platform, region=region, fila=fila,
    )
    st.session_state.perfil_jogador = perfil  # atualiza sidebar/histórico com dados frescos
    dados = obter_dados_jogador(st.session_state.game_name, st.session_state.tag_line,
                                platform, region, fila)
    hist = dados.get("historico") or []
    plano["ultima_verificacao"] = agora.isoformat()

    if not hist:
        return "sem_novidade"
    fim_ts_atual = hist[0].get("fim_ts", 0)
    plano["ultimo_match_id_visto"] = hist[0].get("match_id", "")  # marco da checagem barata

    if perfil.get("amostra_insuficiente"):
        # rota sem amostra confiável → avança o marco, mas não registra medição
        plano["ultimo_fim_ts_visto"] = fim_ts_atual
        return "sem_novidade"

    base_ts = plano.get("baseline_fim_ts")
    if not base_ts:  # plano antigo (passo 4) sem baseline: define o marco agora
        plano["baseline_fim_ts"] = fim_ts_atual
        plano["ultimo_fim_ts_visto"] = fim_ts_atual
        return "baseline"

    visto = plano.get("ultimo_fim_ts_visto", base_ts)
    if fim_ts_atual > visto:  # há partida(s) nova(s) desde a última verificação
        partidas_novas = sum(1 for p in hist if p.get("fim_ts", 0) > base_ts)
        valor = perfil["metricas"].get(plano["metrica"], {}).get("valor_jogador", plano["valor_atual"])
        registrar_medicao(plano, valor, partidas_novas)
        plano["ultimo_fim_ts_visto"] = fim_ts_atual
        return "reavaliou"

    plano["ultimo_fim_ts_visto"] = max(visto, fim_ts_atual)
    return "sem_novidade"


def _mensagem_checkin(plano: dict) -> str:
    """Check-in proativo do tutor (passo 6), exibido na Mentoria após a reavaliação."""
    label = plano["metrica_label"]
    if meta_atingida(plano):
        return (f"Check-in automático: detectei novas partidas suas e seu desempenho em "
                f"**{label}** chegou a {plano['valor_atual']} — você **atingiu a meta** de "
                f"{plano['valor_alvo']}! Mandou muito bem. Quando quiser, geramos um novo "
                f"plano para a sua próxima métrica mais fraca.")
    falta = round(plano["valor_alvo"] - plano["valor_atual"], 2)
    return (f"Check-in automático: vi que você jogou mais partidas. Sua **{label}** está "
            f"em {plano['valor_atual']} (meta {plano['valor_alvo']}, faltam {falta}; "
            f"{descrever_base_plano(plano)}). "
            f"Continue firme nos passos do plano — quer revisar algum ponto comigo?")


@st.fragment(run_every=180)
def _monitor_autonomo():
    """Passo 6: roda periodicamente enquanto o app está aberto. Detecta partidas novas,
    reavalia o plano e faz o tutor dar um check-in proativo — tudo sem botão."""
    plano = st.session_state.get("plano")
    if not plano or plano.get("concluido"):
        return
    tutor_grafo = st.session_state.get("agente_persistente")
    if tutor_grafo is None:
        return
    thread_id = _thread_id()

    status = verificar_partidas_automaticamente(plano)
    if status == "reavaliou":
        st.session_state.mensagens_chat.append(
            {"role": "assistant", "content": _mensagem_checkin(plano)}
        )
        _persistir_plano(plano, tutor_grafo, thread_id)
        st.toast("Reavaliação automática: seu progresso foi atualizado!")
        st.rerun()  # rerun de app: atualiza Mentoria e Plano de Treino
    elif status in ("sem_novidade", "baseline"):
        _persistir_plano(plano, tutor_grafo, thread_id)  # salva o throttle/bookkeeping


@st.dialog("Como executar este exercício")
def _popup_explicar_drill(plano, passo, chave):
    """Popup (modal) com a explicação de COMO executar o drill, gerada pelo tutor a partir do
    campeão/rota/métrica do plano. Cacheia por drill na sessão para não repetir a chamada ao
    LLM a cada interação do modal."""
    st.markdown(f"**{passo.get('descricao', '')}**")
    subs = passo.get("submetas") or []
    if subs:
        st.caption(" · ".join(s.get("descricao", "") for s in subs))
    cache = st.session_state.setdefault("explicacoes_drill", {})
    if chave not in cache:
        try:
            with st.spinner("Analisando seu campeão e o exercício…"):
                cache[chave] = explicar_drill(plano, passo)
        except Exception as e:
            st.warning("Não consegui gerar a explicação agora (o serviço de análise pode "
                       "estar indisponível). Tente de novo em instantes.")
            st.caption(f"Detalhe técnico: {e}")
            return
    st.markdown(cache[chave])


def _render_historico_planos(tutor_grafo, thread_id):
    """Lista os planos anteriores desta rota e permite restaurar qualquer um — cada um traz
    suas próprias medições e ponto de partida. Mostrado com ou sem plano ativo."""
    hist = _historico_planos()
    if not hist:
        return
    with st.expander(f"Planos anteriores ({len(hist)})"):
        st.caption("Volte a um plano anterior sem perder nada: ele guarda as próprias "
                   "medições e o ponto de partida. O plano ativo é arquivado ao restaurar outro.")
        for idx, p in enumerate(hist):
            pct = round(progresso_metrica(p) * 100)
            nmed = len(p.get("medicoes", []))
            atual = p.get("valor_atual", p.get("valor_inicial"))
            badge = " · meta batida" if meta_atingida(p) else ""
            col_txt, col_rest, col_del = st.columns([4, 1, 1])
            col_txt.markdown(
                f"**{p.get('metrica_label', p.get('metrica', ''))}** · "
                f"{p.get('valor_inicial')} → {p.get('valor_alvo')} "
                f"(atual {atual}, {pct}%) · {nmed} reavaliação(ões){badge}  \n"
                f"<small>criado em {p.get('criado_em', '?')}</small>",
                unsafe_allow_html=True,
            )
            chave = f"{assinatura_plano(p)}_{idx}"
            if col_rest.button("Restaurar", key=f"restaurar_{chave}"):
                _restaurar_plano(p, tutor_grafo, thread_id)
                st.rerun()
            if col_del.button("Apagar", key=f"apagar_{chave}"):
                _apagar_do_historico(p)
                st.rerun()


def render_plano_treino(player_profile, tutor_grafo, thread_id):
    st.markdown("---")
    plano = st.session_state.get("plano")

    # Sem amostra suficiente na rota não há "pior métrica" confiável → não dá pra montar meta.
    if player_profile.get("amostra_insuficiente") and not plano:
        st.warning(
            f"Plano indisponível para **{player_profile['posicao_label']}**: só "
            f"{player_profile['partidas_rota']} de {player_profile['minimo_partidas']} "
            "partidas necessárias nessa rota. Jogue mais partidas nela (ou escolha a rota "
            "que você mais joga) para o tutor traçar uma meta confiável."
        )
        return

    if not plano:
        st.info("Defina uma meta concreta e um plano de treino verificável a partir da "
                "sua métrica mais crítica nesta rota.")
        # Próxima métrica a atacar: a mais fraca ainda não dominada nesta rota.
        superadas = _metricas_superadas_rota(player_profile["posicao"])
        alvo = proxima_metrica(player_profile, superadas) or player_profile["pior_metrica_identificada"]
        st.caption(f"Métrica que será o alvo do plano: **{METRIC_LABELS.get(alvo, alvo)}** "
                   f"({descrever_base_comparacao(player_profile)})")
        if st.button("Gerar plano de treino", type="primary"):
            with _carregando("Montando seu plano de treino"):
                _criar_plano(player_profile, tutor_grafo, thread_id)
            st.rerun()
        _render_historico_planos(tutor_grafo, thread_id)
        return

    # Mantém o valor atual da métrica sincronizado com o diagnóstico vigente (gancho passo 5)
    atualizar_valor_atual(plano, player_profile)

    elo_base = _fmt_elo(plano["elo_base"])
    elo_alvo = _fmt_elo(plano["elo_alvo"])
    st.subheader(f"Meta: {plano['metrica_label']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Início", plano["valor_inicial"])
    col2.metric("Atual", plano["valor_atual"],
                delta=round(plano["valor_atual"] - plano["valor_inicial"], 2))
    col3.metric("Alvo", plano["valor_alvo"])
    st.caption(f"Objetivo: alcançar a média de **{plano['metrica_label']}** do elo "
               f"**{elo_alvo}** (um degrau acima do seu **{elo_base}**) · {descrever_base_plano(plano)}.")
    st.progress(progresso_metrica(plano), text="Progresso rumo ao alvo")

    if meta_atingida(plano):
        st.success("Meta atingida! Gere um novo plano para atacar a próxima "
                   "métrica mais fraca.")

    # Tendência das reavaliações (passo 5)
    medicoes = plano.get("medicoes", [])
    if medicoes:
        pontos = [{"Medição": "Início", "Atual": plano["valor_inicial"], "Alvo": plano["valor_alvo"]}]
        for i, m in enumerate(medicoes, 1):
            pontos.append({"Medição": f"#{i} · {m['data']}", "Atual": m["valor"],
                           "Alvo": plano["valor_alvo"]})
        df = pd.DataFrame(pontos)
        # ordem temporal explícita (Início → reavaliações), senão o eixo X é ordenado
        # alfabeticamente e a linha do tempo aparece invertida.
        ordem = df["Medição"].tolist()
        df_long = df.melt(id_vars="Medição", value_vars=["Atual", "Alvo"],
                          var_name="Série", value_name="Valor")
        grafico = alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X("Medição:N", sort=ordem, title=None),
            y=alt.Y("Valor:Q", title=None),
            color=alt.Color("Série:N", title=None),
        )
        st.altair_chart(grafico, width='stretch')
        total_novas = sum(m.get("partidas_novas", 0) for m in medicoes)
        st.caption(f"{len(medicoes)} reavaliação(ões) · {total_novas} partidas novas desde a meta")

    st.markdown("##### Passos do plano")
    st.caption("Cada meta tem sub-metas. Quando você marca todas as sub-metas, a meta "
               "principal é concluída automaticamente.")
    # Chave única por plano E por versão dos drills: garante checkboxes "novos" (zerados) ao
    # trocar exercícios ou restaurar outro plano, em vez de herdar marcações antigas.
    base_key = f"{assinatura_plano(plano)}_{plano['metrica']}_{plano.get('drills_versao', 0)}"
    mudou = False
    for i, passo in enumerate(plano["passos"]):
        subs = passo.get("submetas") or []
        if subs:
            # Meta principal: derivada das sub-metas (conclui sozinha) → checkbox só de leitura.
            # Um checkbox COM key e disabled ignora o argumento `value` nos reruns (mantém o
            # estado inicial). Por isso forçamos o estado via session_state ANTES de criá-lo,
            # a cada rerun — assim ele reflete sempre o passo["concluido"] recalculado.
            meta_key = f"meta_{base_key}_{i}"
            st.session_state[meta_key] = passo["concluido"]
            with st.container(key=f"ajudalinha_{base_key}_{i}"):
                st.checkbox(f"**{passo['descricao']}**", key=meta_key, disabled=True)
                if st.button("?", key=f"ajuda_{base_key}_{i}",
                             help="Como executar este exercício com o seu campeão"):
                    _popup_explicar_drill(plano, passo, f"{base_key}_{i}")
            for j, sub in enumerate(subs):
                espaco, conteudo = st.columns([0.05, 0.95])
                with conteudo:
                    marcado = st.checkbox(sub["descricao"], value=sub["concluido"],
                                          key=f"sub_{base_key}_{i}_{j}")
                if marcado != sub["concluido"]:
                    marcar_submeta(plano, i, j, marcado)
                    mudou = True
            st.write("")
        else:
            # Plano antigo (sem sub-metas): meta principal marcável diretamente.
            with st.container(key=f"ajudalinha_{base_key}_{i}"):
                marcado = st.checkbox(passo["descricao"], value=passo["concluido"],
                                      key=f"passo_{base_key}_{i}")
                if st.button("?", key=f"ajuda_{base_key}_{i}",
                             help="Como executar este exercício com o seu campeão"):
                    _popup_explicar_drill(plano, passo, f"{base_key}_{i}")
            if marcado != passo["concluido"]:
                marcar_passo(plano, i, marcado)
                mudou = True
    if mudou:
        _persistir_plano(plano, tutor_grafo, thread_id)
        st.rerun()

    feitos = sum(1 for p in plano["passos"] if p["concluido"])
    st.caption(f"Concluídos: {feitos}/{len(plano['passos'])} passos · criado em {plano['criado_em']}")

    # Passo 6: a reavaliação é autônoma (sem botão) — o monitor detecta partidas novas
    # e atualiza o progresso sozinho enquanto o app está aberto.
    aviso = "**Reavaliação automática ativa** — detecto novas partidas e atualizo seu progresso sozinho."
    ultima = plano.get("ultima_verificacao")
    if ultima:
        try:
            aviso += f" Última verificação: {datetime.fromisoformat(ultima):%d/%m %H:%M}."
        except ValueError:
            pass
    st.caption(aviso)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    if c1.button("Trocar exercícios",
                 help="Sorteia OUTROS drills para a MESMA meta, mantendo seu progresso, "
                      "medições e histórico de evolução."):
        trocar_drills(plano)
        _persistir_plano(plano, tutor_grafo, thread_id)
        st.rerun()
    if c2.button("Gerar novo plano",
                 help="Cria um plano novo (avança para a próxima métrica quando a meta atual "
                      "é batida). O plano atual fica salvo em 'Planos anteriores'."):
        with _carregando("Montando um novo plano"):
            _criar_plano(player_profile, tutor_grafo, thread_id)
        st.rerun()
    if c3.button("Limpar plano"):
        # Se a meta já foi batida, registra a métrica como dominada ANTES de limpar, para
        # que o próximo plano (mesmo após limpar) ataque a próxima mais fraca, não a mesma.
        if meta_atingida(plano):
            superadas = _metricas_superadas_rota(player_profile["posicao"])
            if plano["metrica"] not in superadas:
                superadas.append(plano["metrica"])
        _arquivar_plano(plano)  # guarda no histórico antes de limpar (restaurável depois)
        _persistir_plano(None, tutor_grafo, thread_id)
        st.rerun()

    _render_historico_planos(tutor_grafo, thread_id)


def _render_insights_evolucao(plano, player_profile, dados, medias_pos, n_pos, rota):
    """Análise em linguagem natural da evolução do jogador (apoio moral + crítica
    construtiva), explicando POR QUE as métricas subiram/caíram a partir das partidas reais.
    Gera uma vez por assinatura (plano + nº de partidas novas) e cacheia na sessão, com um
    botão para forçar a reanálise; assim não gasta uma chamada ao LLM a cada rerun."""
    st.markdown("---")
    st.markdown("##### Análise do tutor sobre sua evolução")

    # Assinatura: muda quando o plano é regenerado ou quando entram partidas novas.
    assinatura = f"{rota}|{plano.get('criado_em')}|{plano.get('metrica')}|{n_pos}"
    cache = st.session_state.setdefault("insights_evolucao", {})

    _, col_btn = st.columns([4, 1])
    with col_btn:
        atualizar = st.button("Atualizar análise", key="btn_insights_evol",
                              width='stretch')

    if atualizar:
        cache.pop(assinatura, None)

    if assinatura not in cache:
        partidas = coletar_partidas_pos_plano(dados, rota, plano.get("baseline_fim_ts"))
        try:
            with _carregando("Analisando sua evolução"):
                cache[assinatura] = gerar_insights_evolucao(
                    plano, player_profile, medias_pos, n_pos, partidas
                )
        except Exception as e:
            st.warning("Não consegui gerar os insights agora (o serviço de análise pode estar "
                       "indisponível). Tente novamente em instantes.")
            st.caption(f"Detalhe técnico: {e}")
            return

    st.markdown(cache[assinatura])
    st.caption("Análise baseada nas suas partidas reais desde o plano — campeões jogados, "
               "resultado e desempenho do time, e composições das equipes.")


def render_evolucao(player_profile, platform, region):
    """Passo 7: aba de evolução. Compara TODAS as métricas da rota no momento em que o
    plano foi aberto (baseline salvo) com as partidas jogadas DEPOIS do plano — mesmo as
    que não são o foco da meta, para o jogador enxergar o impacto geral do treino."""
    st.markdown("---")
    plano = st.session_state.get("plano")
    if not plano:
        st.info("Gere um plano de treino (aba **Plano de Treino**) para começar a "
                "acompanhar a evolução das suas estatísticas.")
        return

    baseline = plano.get("metricas_baseline")
    if not baseline:
        st.warning("Este plano foi criado antes do acompanhamento de evolução, então não há "
                   "um ponto de partida salvo. Clique em **Regenerar plano** na aba *Plano de "
                   "Treino* para registrar o 'antes' e passar a comparar com as próximas partidas.")
        return

    rota = plano["posicao"]
    dados = obter_dados_jogador(st.session_state.game_name, st.session_state.tag_line,
                                platform, region, _fila_atual())
    medias_pos, n_pos = agregar_metricas_rota_periodo(dados, rota, plano.get("baseline_fim_ts"))

    st.subheader(f"Evolução desde o início do treinamento · Rota {ROLE_LABELS.get(rota, rota)}")
    st.caption(
        f"Comparando o momento em que o plano foi aberto (**{plano['criado_em']}**) com "
        f"**{n_pos}** partida(s) jogada(s) depois, nesta rota. "
        f"A métrica-foco do plano está marcada como **(meta do plano)**."
    )

    if n_pos == 0:
        st.info("Você ainda não jogou partidas nesta rota desde que criou o plano. "
                "Jogue algumas e volte aqui — a reavaliação é automática.")
        return

    # Uma st.metric por métrica: valor atual (pós-plano) + delta vs o baseline.
    # Todas as métricas da rota são 'maior = melhor', então delta>0 (verde) = melhora.
    foco = plano.get("metrica")
    itens = list(baseline.items())
    for inicio in range(0, len(itens), 3):
        linha = itens[inicio:inicio + 3]
        for col, (m, base) in zip(st.columns(len(linha)), linha):
            label = METRIC_LABELS.get(m, m.upper().replace("_", " "))
            if m == foco:
                label = f"{label} (meta do plano)"
            antes = base.get("valor")
            depois = medias_pos.get(m)
            if antes is None or depois is None:
                col.metric(label, value="—", delta="sem dados", delta_color="off")
                continue
            col.metric(
                label,
                value=round(depois, 2),
                delta=f"{round(depois - antes, 2):+} vs antes ({round(antes, 2)})",
            )

    st.caption("As barras verdes indicam melhora desde o início do plano; as vermelhas, queda. "
               "Mesmo treinando uma métrica específica, todas são acompanhadas.")

    # Insights do tutor: análise causal da evolução (apoio moral + crítica construtiva),
    # cruzando os movimentos das métricas com as partidas reais (campeão e suas
    # características, elo, desempenho do time e composições).
    _render_insights_evolucao(plano, player_profile, dados, medias_pos, n_pos, rota)

    # Dicas extras: erros mais comuns do elo do jogador (separados por elo).
    erros = erros_comuns_do_elo(player_profile.get("elo_oficial"))
    if erros:
        st.markdown("---")
        st.markdown(f"##### Dicas extras — erros comuns no elo {erros['nome']}")
        for dica in erros["dicas"]:
            st.markdown(f"- {dica}")


@st.dialog("Termos de Uso", width="large")
def _dialogo_termos():
    st.markdown(legal.TERMOS_USO)


@st.dialog("Política de Privacidade", width="large")
def _dialogo_privacidade():
    st.markdown(legal.POLITICA_PRIVACIDADE)


@st.dialog("Minha conta")
def _dialogo_minha_conta():
    """Gestão da conta: exclusão definitiva (LGPD art. 18) com confirmação digitada."""
    st.markdown(f"Conectado como **{st.session_state.user_nome}** "
                f"({'Google' if st.session_state.user_metodo == 'google' else 'conta local'}).")
    st.markdown("---")
    st.markdown("**Excluir minha conta**")
    st.caption("Apaga DEFINITIVAMENTE a conta e todos os dados associados: análises "
               "salvas, conversas com o tutor, planos de treino e sessões de login. "
               "Não há como desfazer.")
    confirmacao = st.text_input('Digite **EXCLUIR** para confirmar:')
    # Validação no CLIQUE (não com disabled=): o valor do campo só chega ao servidor
    # no blur, então um botão desabilitado engoliria o primeiro clique do usuário.
    if st.button("Excluir conta e todos os dados", type="primary", width="stretch"):
        if confirmacao.strip().upper() != "EXCLUIR":
            st.error("Digite EXCLUIR no campo acima para confirmar a exclusão.")
        else:
            excluir_usuario(st.session_state.user_id)
            auth.sair()


def _rodape_legal() -> None:
    """Rodapé de conformidade: disclaimer da Riot (boilerplate obrigatório da política
    de terceiros) + acesso aos Termos/Privacidade + contato."""
    st.markdown("---")
    col_t, col_p, col_c = st.columns([1, 1, 2])
    if col_t.button("Termos de Uso", width="stretch"):
        _dialogo_termos()
    if col_p.button("Política de Privacidade", width="stretch"):
        _dialogo_privacidade()
    col_c.caption(f"Contato: {legal.EMAIL_CONTATO}")
    st.caption("EloRise não é endossado pela Riot Games e não reflete as visões ou "
               "opiniões da Riot Games ou de qualquer pessoa oficialmente envolvida na "
               "produção ou gestão das propriedades da Riot Games. Riot Games e League "
               "of Legends são marcas registradas da Riot Games, Inc.")


# Gerenciamento de estado
if "perfil_jogador" not in st.session_state:
    st.session_state.perfil_jogador = None # Guarda o dicionário real
if "texto_relatorio" not in st.session_state:
    st.session_state.texto_relatorio = None
if "historico_sessao" not in st.session_state:
    st.session_state.historico_sessao = InMemoryChatMessageHistory()
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []
if "tutoria_encerrada" not in st.session_state:
    st.session_state.tutoria_encerrada = False

# Tela inicial (splash): exibida uma única vez por sessão, antes da pesquisa.
if not st.session_state.get("splash_visto", False):
    _tela_inicial()
    st.session_state.splash_visto = True
    time.sleep(3.4)          # tempo da animação antes de revelar a tela de pesquisa
    st.rerun()

# Login: nada além da tela de entrada é acessível sem identificar o usuário — conversas,
# planos e análises ficam salvos POR PERFIL (outro login que pesquise o mesmo nick
# começa do zero, com dados próprios).
_usuario = auth.exigir_login(render_cabecalho=_cabecalho_marca, render_rodape=_rodape_legal)
st.session_state.user_id = _usuario["id"]
st.session_state.user_nome = _usuario["nome"]
st.session_state.user_metodo = _usuario["metodo"]


def _abrir_jogador(game_name: str, tag_line: str, servidor: str, rota: str = None,
                   fila: str = FILA_PADRAO) -> None:
    """Busca o jogador e entra na tela de mentoria (usado pela busca e pelas análises
    salvas do perfil). Registra a análise no perfil do usuário logado."""
    # Higiene da digitação: espaços sobrando e "#" na tag criariam um "jogador novo"
    # (chave/thread diferentes) e duplicariam a análise salva.
    game_name = " ".join(game_name.split())
    tag_line = " ".join(tag_line.split()).lstrip("#")
    fila = fila or FILA_PADRAO
    platform, region = SERVIDORES.get(servidor, list(SERVIDORES.values())[0])
    perfil, relatorio = buscar_perfil_e_formatar(
        game_name, tag_line, rota, platform=platform, region=region, fila=fila
    )
    st.session_state.perfil_jogador = perfil
    st.session_state.texto_relatorio = relatorio
    st.session_state.game_name = game_name
    st.session_state.tag_line = tag_line
    st.session_state.servidor = servidor
    st.session_state.platform = platform
    st.session_state.region = region
    st.session_state.posicao_atual = perfil["posicao"]
    st.session_state.fila_atual = perfil.get("fila", fila)
    # Registra o jogador (com o servidor) na lista de análises salvas do perfil.
    salvar_sessao(st.session_state.user_id, game_name, tag_line,
                  rota=perfil["posicao"], servidor=servidor, fila=st.session_state.fila_atual)


def _voltar_para_busca() -> None:
    """Limpa a sessão preservando o login e o splash e volta à tela de busca
    (limpar tudo derrubaria a sessão do usuário autenticado localmente)."""
    preservar = {c: st.session_state[c]
                 for c in ("auth_user", "splash_visto", "user_id", "user_nome",
                           "user_metodo", "auth_falhas", "auth_ultima_falha")
                 if c in st.session_state}
    st.session_state.clear()
    st.session_state.update(preservar)
    st.rerun()


def _rerun_fragmento() -> None:
    """st.rerun(scope="fragment") com fallback para o rerun de app: o escopo de
    fragmento só é aceito quando a interação veio do próprio fragmento (em runs
    completos — ex.: AppTest — a chamada levanta StreamlitAPIException)."""
    from streamlit.errors import StreamlitAPIException
    try:
        st.rerun(scope="fragment")
    except StreamlitAPIException:
        st.rerun()


@st.fragment
def _render_analises_salvas() -> None:
    """Análises salvas do perfil: retoma um JOGADOR já pesquisado sem digitar o nick de
    novo. A escolha da rota fica para a tela seguinte (seletor "Rota analisada" na
    sidebar); abre na última rota usada, com a conversa e o plano salvos dela.

    É um FRAGMENT: excluir/cancelar reroda só este bloco (scope="fragment") — o clique
    não paga o rerun da página inteira (CSS, panorama etc.). Retomar troca de tela,
    então usa o rerun de app. A lista fica cacheada na sessão para não abrir conexão
    com o banco a cada rerun; a exclusão invalida, e entrar num jogador e voltar passa
    por _voltar_para_busca, que limpa a sessão e força o refetch."""
    if "analises_salvas" not in st.session_state:
        st.session_state.analises_salvas = listar_jogadores(st.session_state.user_id)
    analises_salvas = st.session_state.analises_salvas
    if not analises_salvas:
        return
    st.markdown(f"##### Suas análises salvas ({st.session_state.user_nome})")
    excluir_pendente = st.session_state.get("excluir_analise_pendente")
    colunas = st.columns(3)
    for i, reg in enumerate(analises_salvas[:9]):
        servidor_salvo = reg.get("servidor") or list(SERVIDORES.keys())[0]
        with colunas[i % 3]:
            if excluir_pendente == reg["jogador"]:
                # Confirmação em duas etapas: remove o jogador por completo (perfil,
                # conversas e plano de TODAS as rotas) da lista de jogadores salvos.
                st.warning(f"Excluir a análise de **{nome_exibicao(reg['jogador'])}**? "
                           "O jogador sairá da lista de salvos.")
                col_sim, col_nao = st.columns(2)
                if col_sim.button("Excluir", key=f"conf_excluir_{reg['jogador']}",
                                  type="primary", width="stretch"):
                    nick_gn, nick_tl = reg["jogador"].rsplit("#", 1)
                    excluir_jogador(st.session_state.user_id, nick_gn, nick_tl)
                    st.session_state.pop("excluir_analise_pendente", None)
                    st.session_state.pop("analises_salvas", None)
                    _rerun_fragmento()
                if col_nao.button("Cancelar", key=f"canc_excluir_{reg['jogador']}",
                                  width="stretch"):
                    st.session_state.pop("excluir_analise_pendente", None)
                    _rerun_fragmento()
                continue
            col_abrir, col_excluir = st.columns([5, 1])
            if col_abrir.button(nome_exibicao(reg["jogador"]),
                                key=f"retomar_{reg['jogador']}", width="stretch",
                                help=f"Servidor: {servidor_salvo}"):
                nick_gn, nick_tl = reg["jogador"].rsplit("#", 1)
                with _carregando("Retomando análise salva"):
                    try:
                        _abrir_jogador(nick_gn, nick_tl, servidor_salvo,
                                       rota=reg.get("rota_atual"),
                                       fila=reg.get("fila_atual") or FILA_PADRAO)
                        st.rerun()  # troca de tela: rerun do app inteiro
                    except Exception as e:
                        st.error(f"Erro ao retomar a análise: {e}")
            if col_excluir.button("✕", key=f"excluir_{reg['jogador']}",
                                  help="Excluir esta análise salva"):
                st.session_state.excluir_analise_pendente = reg["jogador"]
                _rerun_fragmento()


# Busca do Jogador
# Se o jogador ainda não foi buscado, exibe um formulário pedindo o Nick
if st.session_state.perfil_jogador is None:
    _cabecalho_marca()
    col_conta, col_minha, col_sair = st.columns([4, 1.2, 1])
    col_conta.caption(f"Conectado como **{st.session_state.user_nome}**")
    if col_minha.button("Minha conta", width="stretch"):
        _dialogo_minha_conta()
    if col_sair.button("Sair", width="stretch"):
        auth.sair()
    st.write("")

    with st.form("busca_jogador"):
        col1, col2, col3 = st.columns([2.4, 1, 1.4])
        with col1:
            game_name = st.text_input("Nick (ex: Jhin Frio)")
        with col2:
            tag_line = st.text_input("Tag (ex: Coffe)")
        with col3:
            servidor = st.selectbox("Servidor", list(SERVIDORES.keys()))

        submit = st.form_submit_button("Analisar Desempenho")

        if submit:
            if game_name and tag_line:
                with _carregando("Consultando histórico de partidas"):
                    try:
                        # Chama a Feature 3, que por sua vez chama a Feature 1
                        _abrir_jogador(game_name, tag_line, servidor)
                        st.rerun() # Recarrega a tela para ir para a Tela 2
                    except Exception as e:
                        st.error(f"Erro ao buscar jogador: Verifique se o Nick está correto ou se a API está online. Detalhes: {e}")
            else:
                st.warning("Preencha o Nick e a Tag.")

    _render_analises_salvas()
    st.markdown("---")
    renderizar_panorama_meta()
    _rodape_legal()
# Interface do tutor
else:
    player_profile = st.session_state.perfil_jogador
    texto_relatorio = st.session_state.texto_relatorio
    
    # Servidor escolhido na busca (fallback BR para sessões antigas)
    platform = st.session_state.get("platform", "br1")
    region = st.session_state.get("region", "americas")
    # Fila ativa (solo/flex/normal): define coleta, benchmarks e o slot de persistência.
    fila = st.session_state.get("fila_atual") or player_profile.get("fila") or FILA_PADRAO
    st.session_state.fila_atual = fila

    # Aquece o índice da base de conhecimento (RAG) uma vez por sessão.
    _aquecer_base_conhecimento()

    # Verifica se o agente já existe na sessão atual
    if "agente_persistente" not in st.session_state:
        # Se não existe, cria a IA e a Memória pela primeira vez e guarda no cofre.
        # O agente recebe os dados brutos e a rota e BUSCA o diagnóstico via ferramentas.
        dados_jogador = obter_dados_jogador(
            st.session_state.game_name, st.session_state.tag_line, platform, region, fila
        )
        # Holder do plano de treino: fonte de verdade compartilhada com as ferramentas
        # do agente (consultar_plano). Restaurado da memória de longo prazo DO USUÁRIO
        # LOGADO (a conversa ativa dele para este jogador/rota/fila), se houver.
        sessao_salva = carregar_sessao(st.session_state.user_id,
                                       st.session_state.game_name, st.session_state.tag_line,
                                       rota=player_profile["posicao"], fila=fila)
        st.session_state.conversa_id = sessao_salva.get("conversa_id")
        caixa_plano = {"plano": sessao_salva.get("plano")}
        grafo, prompt = obter_cadeia_tutor(dados_jogador, player_profile["posicao"], caixa_plano)
        # Memória de longo prazo: restaura a conversa persistida deste jogador
        if sessao_salva.get("mensagens"):
            st.session_state.mensagens_chat = sessao_salva["mensagens"]
            st.session_state.tutoria_encerrada = sessao_salva.get("tutoria_encerrada", False)
            semear_memoria(grafo, prompt, sessao_salva["mensagens"], _thread_id())
        # Plano de treino vive no State do grafo (passo 4)
        semear_plano(grafo, caixa_plano["plano"], _thread_id())
        st.session_state.agente_persistente = grafo
        st.session_state.prompt_sistema = prompt
        st.session_state.caixa_plano = caixa_plano
        st.session_state.plano = caixa_plano["plano"]
        # Métricas já dominadas (por rota): o plano avança para a próxima mais fraca.
        st.session_state.metricas_superadas = sessao_salva.get("metricas_superadas", {})
        # Histórico de planos desta rota (restauráveis com todo o progresso de evolução).
        st.session_state.historico_planos = sessao_salva.get("historico_planos", [])

    # Resgata o agente (com todo o histórico de conversas salvo na RAM)
    tutor_grafo = st.session_state.agente_persistente
    prompt_sistema = st.session_state.prompt_sistema
    # Thread de memória do agente = usuário + jogador + conversa ativa
    thread_id = _thread_id()
    # Não precisa mais do RunnableWithMessageHistory!
    
    def _resetar_estado_conversa():
        """Descarta o estado em RAM do chat/agente para recarregar do disco, no próximo
        rerun, a conversa salva do novo contexto (usado ao trocar de rota)."""
        for chave in ("agente_persistente", "prompt_sistema", "mensagens_chat",
                      "tutoria_encerrada", "plano", "caixa_plano", "historico_planos",
                      "conversa_id"):
            st.session_state.pop(chave, None)

    # Barra lateral de estatísticas
    with st.sidebar:
        st.markdown(
            f"<div class='er-brand-mini'>{_logo_svg(40)}<span class='er-name'>EloRise</span></div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Conectado como **{st.session_state.user_nome}**")
        if st.button("Sair da conta", width="stretch"):
            auth.sair()
        st.title("Perfil")
        st.subheader(nome_exibicao(player_profile['nick']))
        st.caption(f"Servidor: {st.session_state.get('servidor', 'BR (Brasil)')}")

        # Seletor de fila: solo/flex/normal. Trocar REFAZ o fetch da Riot (queue diferente)
        # e compara contra os benchmarks daquela fila. Cada fila tem plano e conversa próprios.
        filas = list(FILAS.keys())
        indice_fila = filas.index(fila) if fila in filas else 0
        fila_escolhida = st.selectbox(
            "Fila:",
            filas,
            index=indice_fila,
            format_func=lambda f: FILAS[f]["label"],
        )
        if fila_escolhida != fila:
            with _carregando(f"Buscando partidas de {FILAS[fila_escolhida]['label']}"):
                # Fila nova = outra queue → novo fetch (a rota detectada pode mudar também).
                perfil, relatorio = buscar_perfil_e_formatar(
                    st.session_state.game_name, st.session_state.tag_line,
                    st.session_state.get("posicao_atual"),
                    platform=platform, region=region, fila=fila_escolhida,
                )
            st.session_state.perfil_jogador = perfil
            st.session_state.texto_relatorio = relatorio
            st.session_state.fila_atual = fila_escolhida
            st.session_state.posicao_atual = perfil["posicao"]
            # Conversa e plano são por (rota, fila): descarta só o estado em RAM para o
            # agente recarregar o slot da nova fila (o da fila anterior segue salvo).
            _resetar_estado_conversa()
            st.rerun()

        # Seletor de rota: permite confirmar/trocar a função analisada
        posicoes = list(ROLE_LABELS.keys())
        indice_atual = posicoes.index(player_profile["posicao"]) if player_profile["posicao"] in posicoes else 0
        rota_escolhida = st.selectbox(
            "Rota analisada:",
            posicoes,
            index=indice_atual,
            format_func=lambda p: ROLE_LABELS.get(p, p),
        )

        # Se o usuário trocou a rota, recalcula o diagnóstico (sem refazer o fetch
        # da Riot) e reinicia o tutor/chat, que dependem do relatório.
        if rota_escolhida != player_profile["posicao"]:
            with _carregando("Recalculando para a nova rota"):
                perfil, relatorio = buscar_perfil_e_formatar(
                    st.session_state.game_name, st.session_state.tag_line, rota_escolhida,
                    platform=platform, region=region, fila=fila
                )
            st.session_state.perfil_jogador = perfil
            st.session_state.texto_relatorio = relatorio
            st.session_state.posicao_atual = rota_escolhida
            # A tutoria e o plano são guardados POR (ROTA, FILA). Ao trocar, NÃO apagamos nada
            # do disco: só descartamos o estado em RAM para o agente recarregar o slot da nova
            # rota. A conversa e o plano da rota anterior continuam salvos, prontos para
            # quando o jogador voltar a ela.
            _resetar_estado_conversa()
            st.rerun()

        st.write(f"**Seu elo:** {_fmt_elo(player_profile['elo_oficial'])}")

        if player_profile.get("amostra_insuficiente"):
            # Sem partidas suficientes NA ROTA → não dá pra comparar métricas com segurança.
            st.markdown("---")
            st.warning(
                f"Amostragem insuficiente em **{player_profile['posicao_label']}**: só "
                f"{player_profile['partidas_rota']} de {player_profile['minimo_partidas']} "
                "partidas necessárias entre as analisadas. Jogue mais partidas nessa rota "
                "(ou selecione a que você mais joga) para uma comparação confiável."
            )
        else:
            # Elo usado como base da comparação "vs Meta" (o oficial, salvo fallback)
            elo_base = player_profile.get("elo_comparacao", player_profile["elo_oficial"])
            elo_fmt = _fmt_elo(elo_base)
            # Posição do jogador DENTRO do elo oficial (percentil na rota inteira) —
            # substitui o antigo "elo equivalente": as distribuições de elos vizinhos
            # se sobrepõem demais para um rótulo de sub-elo honesto.
            percentil = player_profile.get("percentil_geral")
            elo_pct_fmt = _fmt_elo(player_profile.get("elo_percentil", player_profile["elo_oficial"]))
            n_partidas = player_profile.get("partidas_analisadas")
            if percentil is not None:
                # Percentil 34 → "top ~66%" (100 - percentil); a barra preenche pela
                # posição dentro do elo (34%), então mais cheia = melhor.
                st.write(f"**Últimas {n_partidas} partidas (nesta rota):** "
                         f"top ~{100 - percentil}% das métricas de {elo_pct_fmt}")
                st.progress(percentil / 100)
            else:
                st.write(f"**Últimas {n_partidas} partidas analisadas (nesta rota)**")
            st.markdown("---")
            pior = player_profile["pior_metrica_identificada"]
            st.error(f"Ponto crítico: **{METRIC_LABELS.get(pior, pior.upper())}**")
            fila_label_atual = FILAS.get(_fila_atual(), {}).get("label", "esta fila")
            if player_profile.get("base_comparacao", "rota") != "rota":
                campeoes_ref = ", ".join(player_profile.get("campeoes_referencia") or [])
                st.caption(f"Comparação personalizada · referência: média de {elo_fmt} jogando {campeoes_ref or 'seus campeões'}")
            elif player_profile.get("base_degradada"):
                # Queria comparar contra o(s) campeão(ões) do jogador (mono/pool), mas o
                # benchmark daquele campeão NAQUELA FILA não tem amostra suficiente → caiu
                # na média da rota. Deixa o motivo explícito (senão parece que ignorou o main).
                camps = ", ".join(player_profile.get("campeoes_pretendidos") or []) or "seus campeões"
                min_am = player_profile.get("min_amostra_campeao", 20)
                st.info(
                    f"Sem amostra suficiente de **{camps}** em **{fila_label_atual}** ainda "
                    f"(mínimo de {min_am} partidas no seu elo). Comparando com a **média da "
                    f"rota inteira** de {elo_fmt}. Conforme mais partidas dessa fila forem "
                    "coletadas, a comparação passa a ser contra o seu campeão."
                )
            else:
                st.caption(f"Comparado com a média de {elo_fmt} (rota inteira)")

            # Degradação do ELO: o benchmark do elo oficial não tinha amostra, então a
            # comparação usa outro elo — deixa claro para não confundir o usuário.
            if player_profile.get("elo_comparacao_degradado"):
                elo_of_fmt = _fmt_elo(player_profile["elo_oficial"])
                st.caption(f"Obs.: {elo_of_fmt} ainda sem amostra suficiente em "
                           f"{fila_label_atual}; comparando com {elo_fmt}.")

            # Referência COMPLETA no rótulo de cada card: contra quem o diff compara —
            # campeão (mono), pool ou média da rota, sempre com rota + elo.
            # Ex.: "vs Seraphine ADC Master I" | "vs pool ADC Master I" | "vs média ADC Master I"
            rota_curta = {"TOP": "Top", "JUNGLE": "Selva", "MIDDLE": "Meio",
                          "BOTTOM": "ADC", "UTILITY": "Sup"}.get(
                player_profile["posicao"], player_profile["posicao_label"])
            base_ref = player_profile.get("base_comparacao", "rota")
            campeoes_ref_lista = player_profile.get("campeoes_referencia") or []
            if base_ref == "mono" and campeoes_ref_lista:
                ref_rotulo = f"{campeoes_ref_lista[0]} {rota_curta} {elo_fmt}"
            elif base_ref == "pool":
                ref_rotulo = f"pool {rota_curta} {elo_fmt}"
            else:
                ref_rotulo = f"média {rota_curta} {elo_fmt}"

            for metrica, dados in player_profile["metricas"].items():
                label = METRIC_LABELS.get(metrica, metrica.upper().replace("_", " "))
                pct_metrica = dados.get("percentil_elo")
                ajuda = (f"Top ~{100 - pct_metrica}% do {label} de {elo_pct_fmt} nesta rota"
                         if pct_metrica is not None else None)
                valor_exibido = _fmt_valor_metrica(metrica, dados["valor_jogador"])
                if dados["status"] == "N/D":
                    st.metric(label=label, value=valor_exibido, delta="sem referência",
                              delta_color="off", help=ajuda)
                else:
                    st.metric(
                        label=label,
                        value=valor_exibido,
                        delta=f"{dados['diff_pct']}% vs {ref_rotulo}",
                        help=ajuda,
                    )

        st.markdown("---")
        # Botão para analisar outro jogador e resetar a memória da tela.
        if st.button("Pesquisar outro jogador"):
            _voltar_para_busca()
        # Recomeçar do zero: apaga conversas, plano de treino e evolução DESTE jogador
        # (todas as rotas, só para este usuário), mas PRESERVA o perfil — ele continua
        # na lista de jogadores salvos. Volta à busca: a próxima pesquisa parte de uma
        # sessão limpa, com thread novo para o agente.
        if st.session_state.get("confirmar_recomecar"):
            st.warning("Apagar conversas, plano de treino e evolução deste jogador "
                       "e recomeçar do zero? O perfil do jogador será mantido.")
            col_sim, col_nao = st.columns(2)
            if col_sim.button("Apagar tudo", type="primary", width="stretch"):
                limpar_sessao(st.session_state.user_id,
                              st.session_state.game_name, st.session_state.tag_line)
                _voltar_para_busca()
            if col_nao.button("Cancelar", width="stretch"):
                st.session_state.confirmar_recomecar = False
                st.rerun()
        elif st.button("Recomeçar do zero"):
            st.session_state.confirmar_recomecar = True
            st.rerun()

    # Passo 6: monitor autônomo — detecta novas partidas e reavalia o plano sozinho,
    # periodicamente, enquanto o app está aberto (independe da aba ativa).
    _monitor_autonomo()

    # Área principal: abas de Mentoria (chat), Plano, Evolução (se houver plano) e Histórico.
    _hero("EloRise", f"Mentoria personalizada para {nome_exibicao(player_profile['nick'])}")
    tem_plano = bool(st.session_state.get("plano"))
    nomes_abas = (["Mentoria", "Plano de Treino"]
                  + (["Evolução"] if tem_plano else [])
                  + ["Análise de Partidas"])
    abas = dict(zip(nomes_abas, st.tabs(nomes_abas)))

    with abas["Mentoria"]:
        render_mentoria(tutor_grafo, prompt_sistema, player_profile, thread_id)

    with abas["Plano de Treino"]:
        render_plano_treino(player_profile, tutor_grafo, thread_id)

    if "Evolução" in abas:
        with abas["Evolução"]:
            render_evolucao(player_profile, platform, region)

    with abas["Análise de Partidas"]:
        render_historico(obter_historico(
            st.session_state.game_name, st.session_state.tag_line, platform, region, _fila_atual()
        ))

    _rodape_legal()

