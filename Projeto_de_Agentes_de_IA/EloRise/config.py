import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Riot API
# ──────────────────────────────────────────────
# O app usa a PERSONAL key (exclusiva dele; as dev keys ficam com os crawlers da VPS).
# Fallback para RIOT_API_KEY mantém compatibilidade com .env antigos de dev local.
RIOT_API_KEY: str = os.getenv("RIOT_PERSONAL_KEY") or os.getenv("RIOT_API_KEY", "")
PLATFORM: str = os.getenv("LOL_PLATFORM", "br1")
REGION: str = os.getenv("LOL_REGION", "americas")

# Servidores suportados na busca: rótulo → (plataforma, cluster regional).
# A plataforma (ex.: "kr") roteia Summoner/League v4 e também é o filtro `regiao`
# dos benchmarks (a coluna regiao do DB guarda o código de plataforma).
# O cluster roteia Account v1 e Match v5.
SERVIDORES: dict[str, tuple[str, str]] = {
    "BR (Brasil)":            ("br1",  "americas"),
    "NA (Norte-América)":     ("na1",  "americas"),
    "LAN (Lat. Norte)":       ("la1",  "americas"),
    "LAS (Lat. Sul)":         ("la2",  "americas"),
    "KR (Coreia)":            ("kr",   "asia"),
    "JP (Japão)":             ("jp1",  "asia"),
    "EUW (Europa Oeste)":     ("euw1", "europe"),
    "EUNE (Europa Norte/L.)": ("eun1", "europe"),
    "TR (Turquia)":           ("tr1",  "europe"),
    "OCE (Oceania)":          ("oc1",  "americas"),
}

# ──────────────────────────────────────────────
# Identidade do jogador
# ──────────────────────────────────────────────
def nome_exibicao(nick: str) -> str:
    """Nome do jogador para exibir/citar em QUALQUER parte do sistema: só o nome, sem a
    tag (o que vem depois do '#') — ex.: 'Jhin Frio#Coffe' → 'Jhin Frio'. A tag continua
    servindo de identificador interno (chave de sessão, busca na Riot); a UI e o tutor
    citam apenas o nome."""
    return (nick or "").split("#", 1)[0].strip()


# ──────────────────────────────────────────────
# API de Benchmarks (backend FastAPI)
# ──────────────────────────────────────────────
BENCHMARKS_API_URL: str = os.getenv("BENCHMARKS_API_URL", "http://129.213.153.233:8000")

# ──────────────────────────────────────────────
# Coleta de partidas
# ──────────────────────────────────────────────
# Quantas partidas buscar por jogador. 40 ≈ 43 requests/análise — dentro da chave grátis
# da Riot (20 req/seg, 100 req/2min). Suba via env se tiver production key.
MATCH_COUNT: int = int(os.getenv("MATCH_COUNT", "40"))
# Mínimo de partidas NA ROTA para a comparação de métricas ser confiável.
MIN_PARTIDAS_ROTA: int = int(os.getenv("MIN_PARTIDAS_ROTA", "5"))

# ──────────────────────────────────────────────
# Base de comparação consciente do campeão (mono / pool / geral)
# ──────────────────────────────────────────────
# A "fraqueza" do jogador é medida contra a base mais representativa do seu repertório:
#  - MONO: o campeão top cobre >= LIMIAR_MONO_CAMPEAO das partidas da rota, OU há só 1
#          campeão recorrente → compara contra esse campeão.
#  - POOL: 2..MAX_POOL campeões recorrentes → compara contra a média só desses campeões.
#  - GERAL: acima disso (repertório espalhado) → média da rota inteira (comportamento antigo).
# "Recorrente" = campeão com >= MIN_JOGOS_RECORRENTE partidas na rota.
# Base mono/pool só vale se o benchmark do DB tiver >= MIN_AMOSTRA_CAMPEAO amostras no elo.
LIMIAR_MONO_CAMPEAO: float = float(os.getenv("LIMIAR_MONO_CAMPEAO", "0.6"))
MIN_JOGOS_RECORRENTE: int = int(os.getenv("MIN_JOGOS_RECORRENTE", "3"))
MAX_POOL: int = int(os.getenv("MAX_POOL", "5"))
MIN_AMOSTRA_CAMPEAO: int = int(os.getenv("MIN_AMOSTRA_CAMPEAO", "20"))
QUEUE_RANKED_SOLO: int = 420
QUEUE_NORMAL_DRAFT: int = 400
MIN_GAME_DURATION_SECONDS: int = 300

# ──────────────────────────────────────────────
# Filas (seletor solo/flex/normal no Panorama e na página do jogador)
# ──────────────────────────────────────────────
# `queue` = queueId da Riot usado ao buscar as partidas do jogador; a mesma chave
# ('solo'/'flex'/'normal') é passada ao backend como ?fila= para os benchmarks.
FILAS: dict[str, dict] = {
    "solo":   {"queue": 420, "label": "Solo/Duo"},
    "flex":   {"queue": 440, "label": "Flex"},
    "normal": {"queue": 400, "label": "Normal"},
}
FILA_PADRAO: str = "solo"

# ──────────────────────────────────────────────
# Benchmarks
# ──────────────────────────────────────────────
METRICAS: list[str] = ["kda", "cs_min", "ouro_min", "visao_min"]

# ──────────────────────────────────────────────
# Análise personalizada por rota
# ──────────────────────────────────────────────
# Métricas relevantes a cada rota (todas "maior = melhor"), usadas no
# diagnóstico "vs Meta" (o elo equivalente usa ELO_METRICS, abaixo).
ROLE_METRICS: dict[str, list[str]] = {
    "TOP":     ["kda", "cs_min", "ouro_min", "dano_min", "solo_kills", "dano_mitigado", "tempo_cc"],
    "JUNGLE":  ["kda", "cs_jungle_10m", "ouro_min", "visao_min", "dano_objetivos", "kpa", "tempo_cc"],
    "MIDDLE":  ["kda", "cs_min", "ouro_min", "dano_min", "solo_kills", "kpa", "cs_rota_10m"],
    "BOTTOM":  ["kda", "cs_min", "ouro_min", "dano_min", "dano_torres", "pct_dano_time", "cs_rota_10m"],
    "UTILITY": ["kda", "visao_min", "pink_wards", "kpa", "tempo_cc", "cura_total", "dano_mitigado"],
}

# Métricas usadas SÓ no cálculo de elo equivalente: apenas as que CRESCEM de
# forma monotônica com o elo no cache global de benchmarks (Spearman ≥ 0.93
# entre o rank do sub-elo e a média da métrica; 31 sub-elos, ≥18k partidas por
# elo/rota, medido em 07/2026). Métricas do diagnóstico que NÃO passam no corte
# ficam de fora porque são planas ou caem com o elo (ex.: solo_kills tem
# Spearman ≈ -0.997 em todas as rotas; dano_mitigado/tempo_cc/dano_objetivos
# são planas; no Suporte, cs_min e ouro_min caem) — usá-las faria o elo
# estimado CAIR quando o jogador melhora.
ELO_METRICS: dict[str, list[str]] = {
    "TOP":     ["cs_min", "ouro_min", "visao_min", "pink_wards", "cs_rota_10m"],
    "JUNGLE":  ["kda", "cs_min", "ouro_min", "visao_min", "dano_min",
                "pink_wards", "kpa", "cs_jungle_10m", "pct_dano_time"],
    "MIDDLE":  ["cs_min", "ouro_min", "pink_wards", "kpa", "cs_rota_10m"],
    "BOTTOM":  ["cs_min", "ouro_min", "kpa", "cs_rota_10m", "pct_dano_time"],
    "UTILITY": ["kda", "visao_min", "pink_wards", "kpa"],
}

# Nomes amigáveis das rotas (PT-BR)
ROLE_LABELS: dict[str, str] = {
    "TOP": "Top",
    "JUNGLE": "Selva",
    "MIDDLE": "Meio",
    "BOTTOM": "Atirador (ADC)",
    "UTILITY": "Suporte",
}

# Rótulos amigáveis das métricas (para a UI/sidebar)
METRIC_LABELS: dict[str, str] = {
    "kda": "KDA",
    "cs_min": "CS / min",
    "ouro_min": "Ouro / min",
    "visao_min": "Visão / min",
    "dano_min": "Dano / min",
    "dano_objetivos": "Dano a Objetivos",
    "dano_torres": "Dano a Torres",
    "tempo_cc": "Tempo de CC",
    "pink_wards": "Sentinelas de Controle",
    "cura_total": "Cura Total",
    "dano_mitigado": "Dano Mitigado",
    "kpa": "Participação em Abates",
    "solo_kills": "Solo Kills",
    "cs_jungle_10m": "CS Selva (10 min)",
    "cs_rota_10m": "CS Rota (10 min)",
    "pct_dano_time": "% Dano do Time",
}

ELO_ORDER: list[str] = [
    "IRON_IV", "IRON_III", "IRON_II", "IRON_I",
    "BRONZE_IV", "BRONZE_III", "BRONZE_II", "BRONZE_I",
    "SILVER_IV", "SILVER_III", "SILVER_II", "SILVER_I",
    "GOLD_IV", "GOLD_III", "GOLD_II", "GOLD_I",
    "PLATINUM_IV", "PLATINUM_III", "PLATINUM_II", "PLATINUM_I",
    "EMERALD_IV", "EMERALD_III", "EMERALD_II", "EMERALD_I",
    "DIAMOND_IV", "DIAMOND_III", "DIAMOND_II", "DIAMOND_I",
    "MASTER_I", "GRANDMASTER_I", "CHALLENGER_I",
]