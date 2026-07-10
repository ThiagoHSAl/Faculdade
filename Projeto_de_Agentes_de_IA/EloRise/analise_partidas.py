"""
analise_partidas.py — Fase 0 do módulo "Análise de Partidas".

Responsável por:
  1. Buscar e CACHEAR (disco) os dados pesados de uma partida — `match` e
     `timeline` da Match-V5 são IMUTÁVEIS, então buscamos uma vez por match_id
     e nunca mais (pilar da estratégia de rate limit: a timeline é +1 req por
     partida sobre a coleta já existente).
  2. Normalizar a timeline nos eventos que interessam para a reconstrução visual
     2D do jogo (mortes, abates, objetivos, placas, trajetória), já do ponto de
     vista de UM jogador (puuid).
  3. Extrair o "JSON gigante" do match — em especial o objeto `challenges`
     (~150 métricas avançadas) — num perfil rico e organizado em português.

Coordenadas de Summoner's Rift vão de ~0 a ~14820 em x/y (origem no canto
inferior-esquerdo). A normalização para pixel do minimapa fica para a Fase 1.

LIMITAÇÃO conhecida da timeline: eventos de ward (WARD_PLACED/WARD_KILL) NÃO
trazem posição (x,y) — só tipo e autor. Logo, o "mapa de wards" da Fase 4 usará
contagem/timing, não posição exata.
"""

import json
from pathlib import Path

from riot_client import RiotClient


# ──────────────────────────────────────────────────────────────────────────
# Cache em disco (dados imutáveis por match_id)
# ──────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent / "cache_partidas"


def _cache_path(match_id: str, tipo: str) -> Path:
    """Caminho do arquivo de cache. `tipo` ∈ {'match', 'timeline'}."""
    return _CACHE_DIR / f"{match_id}_{tipo}.json"


def _ler_cache(match_id: str, tipo: str) -> dict | None:
    caminho = _cache_path(match_id, tipo)
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None  # cache corrompido → tratado como ausente


def _escrever_cache(match_id: str, tipo: str, dados: dict) -> None:
    try:
        _CACHE_DIR.mkdir(exist_ok=True)
        _cache_path(match_id, tipo).write_text(
            json.dumps(dados, ensure_ascii=False), encoding="utf-8"
        )
    except OSError:
        pass  # falha de escrita de cache nunca deve derrubar a análise


def obter_match(client: RiotClient, match_id: str) -> dict:
    """Dados completos da partida, com cache em disco."""
    cache = _ler_cache(match_id, "match")
    if cache is not None:
        return cache
    dados = client.get_match(match_id)
    _escrever_cache(match_id, "match", dados)
    return dados


def obter_timeline(client: RiotClient, match_id: str) -> dict:
    """Timeline da partida (frames + events), com cache em disco."""
    cache = _ler_cache(match_id, "timeline")
    if cache is not None:
        return cache
    dados = client.get_match_timeline(match_id)
    _escrever_cache(match_id, "timeline", dados)
    return dados


# ──────────────────────────────────────────────────────────────────────────
# Mapeamento puuid → participantId
# ──────────────────────────────────────────────────────────────────────────

def _participant_id(metadata_participants: list[str], puuid: str) -> int | None:
    """participantId (1..10) do puuid, ou None se não estiver na partida.

    A ordem de `metadata.participants` casa com participantId = índice + 1, tanto
    no match quanto na timeline.
    """
    try:
        return metadata_participants.index(puuid) + 1
    except ValueError:
        return None


def _participante_do_puuid(match: dict, puuid: str) -> dict | None:
    for p in match.get("info", {}).get("participants", []):
        if p.get("puuid") == puuid:
            return p
    return None


# ──────────────────────────────────────────────────────────────────────────
# Normalização da timeline (base da reconstrução visual)
# ──────────────────────────────────────────────────────────────────────────

def normalizar_timeline(timeline: dict, puuid: str) -> dict:
    """
    Reduz a timeline crua à perspectiva de UM jogador, pronta para plotar.

    Retorna:
      {
        "participant_id": int,
        "mortes":   [{t_s, x, y, killer_id, assist_ids, bounty}],   # vítima = jogador
        "abates":   [{t_s, x, y, victim_id, assist_ids, bounty}],   # killer = jogador
        "participacoes": [{t_s, x, y, victim_id}],                  # jogador deu assist
        "objetivos": [{t_s, tipo, subtipo, x, y, killer_id, participou, time_id}],
        "placas":    [{t_s, x, y, killer_id, participou, lane}],
        "trajetoria":[{t_s, x, y, ouro_total, xp, nivel, cs}],      # 1 ponto/frame (~60s)
        "wards":     [{t_s, acao, tipo}],   # acao ∈ {colocada, destruida}; SEM posição
      }
    """
    pid = _participant_id(timeline.get("metadata", {}).get("participants", []), puuid)
    info = timeline.get("info", {})
    frames = info.get("frames", [])

    mortes, abates, participacoes = [], [], []
    objetivos, placas, wards, trajetoria = [], [], [], []

    def _pos(ev: dict) -> tuple[int | None, int | None]:
        p = ev.get("position") or {}
        return p.get("x"), p.get("y")

    for frame in frames:
        # Trajetória do jogador (posição + economia ao longo do tempo)
        pf = (frame.get("participantFrames") or {}).get(str(pid))
        if pf:
            pos = pf.get("position") or {}
            trajetoria.append({
                "t_s": frame.get("timestamp", 0) // 1000,
                "x": pos.get("x"), "y": pos.get("y"),
                "ouro_total": pf.get("totalGold", 0),
                "xp": pf.get("xp", 0),
                "nivel": pf.get("level", 0),
                "cs": pf.get("minionsKilled", 0) + pf.get("jungleMinionsKilled", 0),
            })

        for ev in frame.get("events", []):
            tipo = ev.get("type")
            t_s = ev.get("timestamp", 0) // 1000

            if tipo == "CHAMPION_KILL":
                x, y = _pos(ev)
                assist = ev.get("assistingParticipantIds", []) or []
                if ev.get("victimId") == pid:
                    mortes.append({"t_s": t_s, "x": x, "y": y,
                                   "killer_id": ev.get("killerId"),
                                   "assist_ids": assist,
                                   "bounty": ev.get("bounty", 0)})
                elif ev.get("killerId") == pid:
                    abates.append({"t_s": t_s, "x": x, "y": y,
                                   "victim_id": ev.get("victimId"),
                                   "assist_ids": assist,
                                   "bounty": ev.get("bounty", 0)})
                elif pid in assist:
                    participacoes.append({"t_s": t_s, "x": x, "y": y,
                                          "victim_id": ev.get("victimId")})

            elif tipo == "ELITE_MONSTER_KILL":
                x, y = _pos(ev)
                assist = ev.get("assistingParticipantIds", []) or []
                objetivos.append({
                    "t_s": t_s, "tipo": ev.get("monsterType"),
                    "subtipo": ev.get("monsterSubType"),
                    "x": x, "y": y, "killer_id": ev.get("killerId"),
                    "time_id": ev.get("killerTeamId"),
                    "participou": ev.get("killerId") == pid or pid in assist,
                })

            elif tipo == "BUILDING_KILL":
                x, y = _pos(ev)
                assist = ev.get("assistingParticipantIds", []) or []
                objetivos.append({
                    "t_s": t_s, "tipo": ev.get("buildingType"),
                    "subtipo": ev.get("towerType") or ev.get("laneType"),
                    "x": x, "y": y, "killer_id": ev.get("killerId"),
                    "time_id": ev.get("teamId"),
                    "participou": ev.get("killerId") == pid or pid in assist,
                })

            elif tipo == "TURRET_PLATE_DESTROYED":
                x, y = _pos(ev)
                placas.append({"t_s": t_s, "x": x, "y": y,
                               "killer_id": ev.get("killerId"),
                               "participou": ev.get("killerId") == pid,
                               "lane": ev.get("laneType")})

            elif tipo == "WARD_PLACED" and ev.get("creatorId") == pid:
                wards.append({"t_s": t_s, "acao": "colocada",
                              "tipo": ev.get("wardType")})
            elif tipo == "WARD_KILL" and ev.get("killerId") == pid:
                wards.append({"t_s": t_s, "acao": "destruida",
                              "tipo": ev.get("wardType")})

    return {
        "participant_id": pid,
        "mortes": mortes,
        "abates": abates,
        "participacoes": participacoes,
        "objetivos": objetivos,
        "placas": placas,
        "trajetoria": trajetoria,
        "wards": wards,
    }


# ──────────────────────────────────────────────────────────────────────────
# Fase 2 — contexto de cada morte (death recap)
# ──────────────────────────────────────────────────────────────────────────

# Raios em unidades de jogo (SR ~14800 de largura). ~2500 ≈ alcance de um teamfight.
_RAIO_PROXIMO = 2500
_RAIO_ISOLADO = 2800


def _time_do_pid(pid: int) -> int:
    """Time de um participantId: 1-5 → 100 (azul), 6-10 → 200 (vermelho)."""
    return 100 if pid <= 5 else 200


def _frame_mais_proximo(frames: list[dict], t_ms: int) -> dict | None:
    return min(frames, key=lambda f: abs(f.get("timestamp", 0) - t_ms)) if frames else None


def contexto_morte(timeline: dict, puuid: str, morte: dict) -> dict:
    """
    Contextualiza UMA morte usando o frame da timeline mais próximo do evento:
    isolamento do time, desvantagem numérica (gank) e déficit de ouro/nível
    contra quem matou. Frames são ~1/min, então é uma aproximação (boa o bastante
    para o "porquê" da morte). Devolve {} se faltar dado.
    """
    pid = _participant_id(timeline.get("metadata", {}).get("participants", []), puuid)
    frames = timeline.get("info", {}).get("frames", [])
    dx, dy = morte.get("x"), morte.get("y")
    if pid is None or dx is None or dy is None:
        return {}
    frame = _frame_mais_proximo(frames, morte.get("t_s", 0) * 1000)
    if not frame:
        return {}
    pframes = frame.get("participantFrames", {}) or {}

    meu_time = _time_do_pid(pid)
    aliados = [i for i in range(1, 11) if i != pid and _time_do_pid(i) == meu_time]
    inimigos = [i for i in range(1, 11) if _time_do_pid(i) != meu_time]

    def _dist(i: int) -> float | None:
        pos = (pframes.get(str(i)) or {}).get("position") or {}
        x, y = pos.get("x"), pos.get("y")
        if x is None or y is None:
            return None
        return ((x - dx) ** 2 + (y - dy) ** 2) ** 0.5

    dists_aliados = [d for i in aliados if (d := _dist(i)) is not None]
    aliados_perto = sum(1 for d in dists_aliados if d <= _RAIO_PROXIMO)
    inimigos_perto = sum(1 for i in inimigos if (d := _dist(i)) is not None and d <= _RAIO_PROXIMO)
    aliado_mais_perto = min(dists_aliados) if dists_aliados else None

    eu = pframes.get(str(pid)) or {}
    killer_id = morte.get("killer_id")
    killer = pframes.get(str(killer_id)) or {} if killer_id else {}
    ouro_eu, ouro_k = eu.get("totalGold"), killer.get("totalGold")
    nivel_eu, nivel_k = eu.get("level"), killer.get("level")

    return {
        "aliados_perto": aliados_perto,
        "inimigos_perto": inimigos_perto,
        "aliado_mais_perto": round(aliado_mais_perto) if aliado_mais_perto is not None else None,
        "isolado": aliado_mais_perto is None or aliado_mais_perto > _RAIO_ISOLADO,
        "outnumbered": inimigos_perto >= aliados_perto + 2,
        "deficit_ouro": (ouro_k - ouro_eu) if (ouro_eu is not None and ouro_k is not None) else None,
        "deficit_nivel": (nivel_k - nivel_eu) if (nivel_eu is not None and nivel_k is not None) else None,
    }


def enriquecer_objetivos(timeline: dict, puuid: str, team_id: int,
                         objetivos: list[dict]) -> list[dict]:
    """
    Fase 5: para cada objetivo, adiciona se foi do SEU time, a posição do jogador
    no frame mais próximo do evento e a distância dele até o objetivo — base do
    "onde você estava quando o objetivo caiu". `objetivos` no formato de
    `normalizar_timeline`.
    """
    pid = _participant_id(timeline.get("metadata", {}).get("participants", []), puuid)
    frames = timeline.get("info", {}).get("frames", [])
    out = []
    for obj in objetivos:
        e = dict(obj)
        e["seu_time"] = obj.get("time_id") == team_id
        ux = uy = dist = None
        if pid is not None:
            frame = _frame_mais_proximo(frames, obj.get("t_s", 0) * 1000)
            if frame:
                pos = (frame.get("participantFrames", {}).get(str(pid)) or {}).get("position") or {}
                ux, uy = pos.get("x"), pos.get("y")
                if ux is not None and obj.get("x") is not None:
                    dist = round(((ux - obj["x"]) ** 2 + (uy - obj["y"]) ** 2) ** 0.5)
        e["jogador_x"], e["jogador_y"], e["dist_jogador"] = ux, uy, dist
        out.append(e)
    return out


def metricas_posicionamento(trajetoria: list[dict], team_id: int) -> dict:
    """
    Métrica de exposição (Fase 3) a partir da trajetória (~1 ponto/min): fração
    do tempo no CAMPO INIMIGO. A anti-diagonal x+y = ~14870 separa a metade
    inferior-esquerda (base azul, time 100) da superior-direita (base vermelha,
    time 200). Aproximação grosseira (granularidade de 1 min), serve de proxy de
    agressividade/overextend.
    """
    pts = [p for p in trajetoria if p.get("x") is not None and p.get("y") is not None]
    if not pts:
        return {}
    meio = 14870  # anti-diagonal que separa as duas metades do mapa
    if team_id == 100:
        no_inimigo = sum(1 for p in pts if (p["x"] + p["y"]) > meio)
    else:
        no_inimigo = sum(1 for p in pts if (p["x"] + p["y"]) < meio)
    return {"frames": len(pts), "pct_campo_inimigo": round(100 * no_inimigo / len(pts))}


def descrever_contexto_morte(ctx: dict, nome_killer: str | None = None) -> list[str]:
    """Transforma o contexto numa lista de frases curtas (tooltip/agente)."""
    if not ctx:
        return []
    linhas = []
    if ctx.get("outnumbered"):
        linhas.append(f"Pego em desvantagem ({ctx['aliados_perto'] + 1}v{ctx['inimigos_perto']})")
    elif ctx.get("isolado"):
        linhas.append("Isolado do time")
    d = ctx.get("deficit_ouro")
    if d and d >= 500 and nome_killer:
        linhas.append(f"{d} de ouro atrás de {nome_killer}")
    dn = ctx.get("deficit_nivel")
    if dn and dn >= 1 and nome_killer:
        plural = "níveis" if dn > 1 else "nível"
        linhas.append(f"{dn} {plural} atrás de {nome_killer}")
    return linhas


# ──────────────────────────────────────────────────────────────────────────
# Fase 6 — padrões entre partidas (alimenta o tutor e o plano)
# ──────────────────────────────────────────────────────────────────────────

def _rotulo_regiao(x: float, y: float) -> str:
    """Rótulo grosseiro de região do mapa (grade 3x3) para descrever um cluster."""
    col = "esquerda" if x < 5000 else "centro" if x < 9800 else "direita"
    lin = "inferior" if y < 5000 else "meio" if y < 9800 else "superior"
    return f"{lin}-{col}"


def clusterizar_mortes(mortes: list[dict], raio: int = 1600) -> list[dict]:
    """Agrupa mortes próximas (greedy, média corrente) → locais recorrentes.
    Retorna clusters {cx, cy, n} ordenados do mais frequente ao menos."""
    clusters: list[dict] = []
    for m in mortes:
        x, y = m.get("x"), m.get("y")
        if x is None or y is None:
            continue
        for c in clusters:
            if ((c["cx"] - x) ** 2 + (c["cy"] - y) ** 2) ** 0.5 <= raio:
                n = c["n"]
                c["cx"] = (c["cx"] * n + x) / (n + 1)
                c["cy"] = (c["cy"] * n + y) / (n + 1)
                c["n"] = n + 1
                break
        else:
            clusters.append({"cx": float(x), "cy": float(y), "n": 1})
    for c in clusters:
        c["cx"], c["cy"] = round(c["cx"]), round(c["cy"])
    clusters.sort(key=lambda c: -c["n"])
    return clusters


def resumo_padroes(client: RiotClient, partidas: list[dict], puuid: str,
                   team_id: int, limite: int = 5) -> dict:
    """
    Agrega padrões das últimas `limite` partidas: mortes e seus contextos, clusters de
    local de morte, participação em objetivos épicos, exposição no campo inimigo E, do
    match cacheado, médias de desempenho (cs/min, dano/min, visão/min, tempo morto) e a
    vantagem de lane @10 (ouro/cs). Base da Fase 6 (tutor + plano).
    """
    mortes_all, deficit_ouro, pct_inimigo = [], [], []
    cs_min, dano_min, vis_min, tempo_morto, ouro10, cs10 = [], [], [], [], [], []
    n_part = isolado = outnumbered = obj_total = obj_part = 0

    def _media(xs, casas=1):
        return round(sum(xs) / len(xs), casas) if xs else None

    for p in partidas[:limite]:
        mid = p.get("match_id")
        if not mid:
            continue
        try:
            tl = obter_timeline(client, mid)
        except Exception:
            continue
        dados = normalizar_timeline(tl, puuid)
        n_part += 1
        for m in dados["mortes"]:
            if m.get("x") is None:
                continue
            mortes_all.append({"x": m["x"], "y": m["y"], "t_s": m["t_s"]})
            ctx = contexto_morte(tl, puuid, m)
            if ctx.get("isolado"):
                isolado += 1
            if ctx.get("outnumbered"):
                outnumbered += 1
            if ctx.get("deficit_ouro") is not None:
                deficit_ouro.append(ctx["deficit_ouro"])
        for o in dados["objetivos"]:
            if o["tipo"] in ("DRAGON", "BARON_NASHOR", "RIFTHERALD") and o.get("time_id") == team_id:
                obj_total += 1
                if o.get("participou"):
                    obj_part += 1
        mp = metricas_posicionamento(dados["trajetoria"], team_id)
        if mp:
            pct_inimigo.append(mp["pct_campo_inimigo"])
        # Métricas ricas do match (cacheado) + vantagem de lane @10.
        try:
            match = obter_match(client, mid)
            ricos = extrair_dados_ricos(match, puuid)
            if ricos:
                cs_min.append(ricos["economia"]["cs_min"])
                dano_min.append(ricos["combate"]["dano_por_min"])
                vis_min.append(ricos["visao"]["vision_min"])
                tempo_morto.append(ricos["sobrevivencia"]["tempo_morto_s"])
            st_ = series_temporais(tl, match, puuid, team_id)
            m10 = (st_.get("marcos") or {}).get("10") if st_ else None
            if m10:
                ouro10.append(m10["ouro"])
                cs10.append(m10["cs"])
        except Exception:
            pass
    return {
        "partidas": n_part,
        "mortes": len(mortes_all),
        "isolado": isolado,
        "outnumbered": outnumbered,
        "deficit_ouro_medio": round(sum(deficit_ouro) / len(deficit_ouro)) if deficit_ouro else None,
        "obj_epicos_time": obj_total,
        "obj_participou": obj_part,
        "pct_campo_inimigo_medio": round(sum(pct_inimigo) / len(pct_inimigo)) if pct_inimigo else None,
        "cs_min_medio": _media(cs_min),
        "dano_min_medio": _media(dano_min, 0),
        "vision_min_medio": _media(vis_min, 2),
        "tempo_morto_medio": _media(tempo_morto, 0),
        "ouro_diff10_medio": _media(ouro10, 0),
        "cs_diff10_medio": _media(cs10, 1),
        "clusters": clusterizar_mortes(mortes_all),
        "mortes_pontos": mortes_all,
    }


def descrever_padroes(r: dict) -> list[str]:
    """Insights em texto a partir de `resumo_padroes` (para a UI e o agente)."""
    if not r or not r.get("partidas"):
        return ["Sem partidas analisadas."]
    L = [f"{r['partidas']} partidas analisadas, {r['mortes']} mortes no total."]
    n = r["mortes"]
    if n:
        if r["outnumbered"]:
            L.append(f"{r['outnumbered']} mortes ({round(100 * r['outnumbered'] / n)}%) em "
                     "desvantagem numérica — atenção a ganks e a agrupar sem visão.")
        if r["isolado"]:
            L.append(f"{r['isolado']} mortes ({round(100 * r['isolado'] / n)}%) isolado do time.")
        if r.get("deficit_ouro_medio") and r["deficit_ouro_medio"] > 0:
            L.append(f"Na média, morreu {r['deficit_ouro_medio']} de ouro atrás de quem te matou.")
        top = (r.get("clusters") or [None])[0]
        if top and top["n"] >= 3:
            L.append(f"Local recorrente de morte: {top['n']} mortes na região "
                     f"{_rotulo_regiao(top['cx'], top['cy'])} do mapa.")
    if r.get("obj_epicos_time"):
        L.append(f"Participou de {r['obj_participou']}/{r['obj_epicos_time']} objetivos "
                 "épicos do seu time.")
    if r.get("pct_campo_inimigo_medio") is not None:
        L.append(f"Passou em média {r['pct_campo_inimigo_medio']}% do tempo no campo inimigo.")
    if r.get("ouro_diff10_medio") is not None:
        sinal = "à frente" if r["ouro_diff10_medio"] >= 0 else "atrás"
        L.append(f"Aos 10 min, em média {abs(int(r['ouro_diff10_medio']))} de ouro {sinal} do "
                 f"oponente de lane (CS {r.get('cs_diff10_medio'):+g}).")
    medias = []
    if r.get("cs_min_medio") is not None:
        medias.append(f"{r['cs_min_medio']:g} CS/min")
    if r.get("dano_min_medio") is not None:
        medias.append(f"{int(r['dano_min_medio'])} dano/min")
    if r.get("vision_min_medio") is not None:
        medias.append(f"{r['vision_min_medio']} visão/min")
    if medias:
        L.append("Médias do período: " + " · ".join(medias) + ".")
    if r.get("tempo_morto_medio"):
        L.append(f"Tempo morto médio por partida: {round(r['tempo_morto_medio'] / 60, 1)} min.")
    return L


# ──────────────────────────────────────────────────────────────────────────
# Extração rica do match JSON (o "JSON gigante" — challenges & cia.)
# ──────────────────────────────────────────────────────────────────────────

# Pings = sinal COMPORTAMENTAL forte (comunicação/macro), pouco explorado.
_PINGS = [
    "allInPings", "assistMePings", "basicPings", "commandPings", "dangerPings",
    "enemyMissingPings", "enemyVisionPings", "getBackPings", "holdPings",
    "needVisionPings", "onMyWayPings", "pushPings", "retreatPings",
    "visionClearedPings",
]


def extrair_dados_ricos(match: dict, puuid: str) -> dict:
    """
    Extrai um perfil rico do jogador a partir do match JSON completo — muito além
    das médias por rota já calculadas. Tudo defensivo (.get): o objeto
    `challenges` varia por patch. `challenges_raw` carrega o dump completo para
    quem quiser cavar mais fundo sem novo deploy.
    """
    p = _participante_do_puuid(match, puuid)
    if not p:
        return {}

    info = match.get("info", {})
    chal = p.get("challenges", {}) or {}
    dur_s = info.get("gameDuration", 0) or 1
    dur_min = dur_s / 60
    cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
    k, d, a = p.get("kills", 0), p.get("deaths", 0), p.get("assists", 0)

    return {
        "combate": {
            "kills": k, "deaths": d, "assists": a,
            "kda": round((k + a) / max(1, d), 2),
            "kill_participation": chal.get("killParticipation", 0),
            "double_kills": p.get("doubleKills", 0),
            "triple_kills": p.get("tripleKills", 0),
            "quadra_kills": p.get("quadraKills", 0),
            "penta_kills": p.get("pentaKills", 0),
            "maior_multikill": p.get("largestMultiKill", 0),
            "maior_sequencia_abates": p.get("largestKillingSpree", 0),
            "solo_kills": chal.get("soloKills", 0),
            "dano_campeoes": p.get("totalDamageDealtToChampions", 0),
            "dano_fisico": p.get("physicalDamageDealtToChampions", 0),
            "dano_magico": p.get("magicDamageDealtToChampions", 0),
            "dano_verdadeiro": p.get("trueDamageDealtToChampions", 0),
            "dano_por_min": chal.get("damagePerMinute", 0),
            "pct_dano_time": chal.get("teamDamagePercentage", 0),
            "dano_recebido": p.get("totalDamageTaken", 0),
            "dano_mitigado": p.get("damageSelfMitigated", 0),
            "maior_critico": p.get("largestCriticalStrike", 0),
            "cura_total": p.get("totalHeal", 0),
            "cura_aliados": p.get("totalHealsOnTeammates", 0),
            "escudo_aliados": p.get("totalDamageShieldedOnTeammates", 0),
            "tempo_cc_aplicado_s": p.get("timeCCingOthers", 0),
            "imobilizacoes_inimigos": chal.get("enemyChampionImmobilizations", 0),
        },
        "economia": {
            "ouro": p.get("goldEarned", 0),
            "ouro_min": round(p.get("goldEarned", 0) / dur_min, 1),
            "ouro_gasto": p.get("goldSpent", 0),
            "ouro_por_min_chal": chal.get("goldPerMinute", 0),
            "cs": cs,
            "cs_min": round(cs / dur_min, 1),
            "cs_neutro": p.get("neutralMinionsKilled", 0),
            "cs_rota_10m": chal.get("laneMinionsFirst10Minutes", 0),
            "cs_jungle_10m": chal.get("jungleCsBefore10Minutes", 0),
            "vantagem_cs_max_oponente": chal.get("maxCsAdvantageOnLaneOpponent", 0),
        },
        "visao": {
            "vision_score": p.get("visionScore", 0),
            "vision_min": chal.get("visionScorePerMinute", 0),
            "wards_colocadas": p.get("wardsPlaced", 0),
            "wards_destruidas": p.get("wardsKilled", 0),
            "pink_wards_compradas": p.get("visionWardsBoughtInGame", 0),
            "control_wards": chal.get("controlWardsPlaced", 0),
            "detector_wards": p.get("detectorWardsPlaced", 0),
            "ward_takedowns": chal.get("wardTakedowns", 0),
            "ward_takedowns_antes_20m": chal.get("wardTakedownsBefore20M", 0),
            "vantagem_visao_oponente": chal.get("visionScoreAdvantageLaneOpponent", 0),
        },
        "objetivos": {
            "dragoes": p.get("dragonKills", 0),
            "baroes": p.get("baronKills", 0),
            "arautos": chal.get("riftHeraldTakedowns", 0),
            "torres_destruidas": p.get("turretKills", 0),
            "torres_takedowns": p.get("turretTakedowns", 0),
            "inibidores": p.get("inhibitorKills", 0),
            "placas_torre": chal.get("turretPlatesTaken", 0),
            "scuttle": chal.get("scuttleCrabKills", 0),
            "dano_objetivos": p.get("damageDealtToObjectives", 0),
            "dano_torres": p.get("damageDealtToBuildings", 0),
            "objetivos_roubados": p.get("objectivesStolen", 0),
            "monstros_epicos_roubados": chal.get("epicMonsterSteals", 0),
        },
        "sobrevivencia": {
            "tempo_morto_s": p.get("totalTimeSpentDead", 0),
            "maior_tempo_vivo_s": p.get("longestTimeSpentLiving", 0),
            "nivel": p.get("champLevel", 0),
            "xp": p.get("champExperience", 0),
            "sobreviveu_hp_critico": chal.get("survivedSingleDigitHpCount", 0),
            "sobreviveu_3_imobilizacoes": chal.get("survivedThreeImmobilizesInFight", 0),
            "dano_grande_sobrevivido": chal.get("tookLargeDamageSurvived", 0),
        },
        "habilidade": {
            "skillshots_acertados": chal.get("skillshotsHit", 0),
            "skillshots_desviados": chal.get("skillshotsDodged", 0),
            "abates_em_desvantagem": chal.get("outnumberedKills", 0),
            "quick_solo_kills": chal.get("quickSoloKills", 0),
            "kills_perto_torre_inimiga": chal.get("killsNearEnemyTurret", 0),
            "kills_sob_torre_propria": chal.get("killsUnderOwnTurret", 0),
            "usos_habilidade": chal.get("abilityUses", 0),
            "takedowns_primeiros_25m": chal.get("takedownsFirst25Minutes", 0),
        },
        "lane": {
            "posicao_time": p.get("teamPosition", ""),
            "posicao_individual": p.get("individualPosition", ""),
            "vantagem_ouro_xp_lane": chal.get("laningPhaseGoldExpAdvantage", 0),
            "vantagem_ouro_xp_early": chal.get("earlyLaningPhaseGoldExpAdvantage", 0),
            "vantagem_nivel_max_oponente": chal.get("maxLevelLeadLaneOpponent", 0),
        },
        "comportamento_pings": {ping: p.get(ping, 0) for ping in _PINGS},
        "construcao": {
            "itens": [p.get(f"item{i}", 0) for i in range(7)],
            "itens_comprados": p.get("itemsPurchased", 0),
            "summoner_spells": [p.get("summoner1Id", 0), p.get("summoner2Id", 0)],
            "summoner_casts": [p.get("summoner1Casts", 0), p.get("summoner2Casts", 0)],
            "spell_casts": [p.get(f"spell{i}Casts", 0) for i in range(1, 5)],
            "runas": p.get("perks", {}),
        },
        "contexto": {
            "vitoria": bool(p.get("win")),
            "duracao_s": dur_s,
            "fila_id": info.get("queueId"),
            "patch": info.get("gameVersion", ""),
            "first_blood": bool(p.get("firstBloodKill")),
            "first_tower": bool(p.get("firstTowerKill")),
            "rendeu": bool(p.get("gameEndedInSurrender")),
            "rendeu_cedo": bool(p.get("gameEndedInEarlySurrender")),
        },
        "challenges_raw": chal,
    }


def resumo_times(match: dict) -> list[dict]:
    """Resumo por time: vitória, bans e contagem de objetivos (baron/dragão/etc.)."""
    times = []
    for t in match.get("info", {}).get("teams", []):
        obj = t.get("objectives", {}) or {}
        times.append({
            "time_id": t.get("teamId"),
            "vitoria": bool(t.get("win")),
            "bans": [b.get("championId") for b in t.get("bans", [])],
            "objetivos": {nome: {"primeiro": v.get("first", False),
                                 "quantidade": v.get("kills", 0)}
                          for nome, v in obj.items()},
        })
    return times


# ──────────────────────────────────────────────────────────────────────────
# Conveniência: pacote completo de análise de uma partida para um jogador
# ──────────────────────────────────────────────────────────────────────────

def analisar_partida(client: RiotClient, match_id: str, puuid: str) -> dict:
    """Junta tudo da Fase 0: dados ricos + timeline normalizada + times.

    Ponto de entrada único para a UI/agente. Usa cache de disco em ambas as
    chamadas de rede, então repetir a análise da mesma partida é instantâneo.
    """
    match = obter_match(client, match_id)
    timeline = obter_timeline(client, match_id)
    return {
        "match_id": match_id,
        "ricos": extrair_dados_ricos(match, puuid),
        "timeline": normalizar_timeline(timeline, puuid),
        "times": resumo_times(match),
    }


def _perfil_por_pid(match: dict) -> dict[int, dict]:
    """participantId (1..10) → {champ, rota} a partir do match."""
    parts = match.get("info", {}).get("participants", [])
    por_puuid = {p.get("puuid"): {"champ": p.get("championName", "?"),
                                  "rota": p.get("teamPosition") or p.get("individualPosition") or ""}
                 for p in parts}
    meta = match.get("metadata", {}).get("participants", [])
    return {i: por_puuid.get(pu, {"champ": "?", "rota": ""}) for i, pu in enumerate(meta, start=1)}


def _fase_jogo(t_s: int) -> str:
    """Fase do jogo de um evento (s): fase de rotas / meio / fim."""
    if t_s < 14 * 60:
        return "fase de rotas (early)"
    if t_s < 25 * 60:
        return "meio de jogo"
    return "fim de jogo"


def _grupo_rota(rota: str) -> str:
    """Lane de uma posição. BOTTOM e UTILITY (atirador + suporte) dividem a BOT,
    então ambos são oponentes de lane um do outro num confronto 2v2."""
    r = (rota or "").upper()
    if r in ("BOTTOM", "UTILITY"):
        return "BOT"
    return r or "?"


# ──────────────────────────────────────────────────────────────────────────
# Séries temporais (evolução vs oponente de lane) e build/skill order
# Aproveitam dados da timeline hoje subusados: participantFrames de TODOS os
# jogadores (ouro/xp/cs por minuto) e os eventos ITEM_*/SKILL_LEVEL_UP.
# ──────────────────────────────────────────────────────────────────────────

_SLOT_LABEL = {1: "Q", 2: "W", 3: "E", 4: "R"}


def _oponentes_de_lane(match: dict, puuid: str, team_id: int) -> list[int]:
    """participantIds do(s) oponente(s) de lane no time inimigo. Casa a posição
    EXATA (BOTTOM×BOTTOM, UTILITY×UTILITY → 1 oponente direto); só se nada casar
    cai no grupo de lane (`_grupo_rota`, ex.: BOT inteira)."""
    parts = match.get("info", {}).get("participants", [])
    meta = match.get("metadata", {}).get("participants", [])
    pid_de = {pu: i for i, pu in enumerate(meta, start=1)}
    eu = _participante_do_puuid(match, puuid)
    if not eu:
        return []
    minha_pos = (eu.get("teamPosition") or eu.get("individualPosition") or "").upper()
    meu_grupo = _grupo_rota(minha_pos)
    exatos, grupo = [], []
    for p in parts:
        if p.get("teamId") == team_id:
            continue
        pos = (p.get("teamPosition") or p.get("individualPosition") or "").upper()
        pid = pid_de.get(p.get("puuid"))
        if pid is None or not pos:
            continue
        if pos == minha_pos:
            exatos.append(pid)
        elif _grupo_rota(pos) == meu_grupo:
            grupo.append(pid)
    return exatos or grupo


def series_temporais(timeline: dict, match: dict, puuid: str, team_id: int) -> dict:
    """
    Série por minuto da DIFERENÇA de ouro/xp/cs do jogador contra o oponente de lane
    (jogador − oponente), a partir dos participantFrames da timeline (dados de TODOS
    os jogadores, hoje subusados). Casa o oponente direto pela posição; na falta de
    casamento, soma o grupo de lane (BOT). Devolve a série + marcos (@10, @14, fim) e
    o maior pico/vale de ouro — base do gráfico de evolução e do dossiê (evolucao_lane).
    """
    pid = _participant_id(timeline.get("metadata", {}).get("participants", []), puuid)
    frames = timeline.get("info", {}).get("frames", [])
    op_pids = _oponentes_de_lane(match, puuid, team_id)
    if pid is None or not frames or not op_pids:
        return {}

    def _cs(pf: dict) -> int:
        return pf.get("minionsKilled", 0) + pf.get("jungleMinionsKilled", 0)

    serie = []
    for fr in frames:
        pfs = fr.get("participantFrames") or {}
        meu = pfs.get(str(pid))
        ops = [pfs.get(str(o)) for o in op_pids if pfs.get(str(o))]
        if not meu or not ops:
            continue
        serie.append({
            "t_s": fr.get("timestamp", 0) // 1000,
            "ouro_diff": meu.get("totalGold", 0) - sum(o.get("totalGold", 0) for o in ops),
            "xp_diff": meu.get("xp", 0) - sum(o.get("xp", 0) for o in ops),
            "cs_diff": _cs(meu) - sum(_cs(o) for o in ops),
        })
    if not serie:
        return {}

    def _em(t_min: int) -> dict | None:
        cand = [p for p in serie if p["t_s"] <= t_min * 60 + 30]
        return cand[-1] if cand else None

    marcos = {}
    for nome, mins in (("10", 10), ("14", 14)):
        p = _em(mins)
        if p:
            marcos[nome] = {"ouro": p["ouro_diff"], "xp": p["xp_diff"], "cs": p["cs_diff"]}
    fim = serie[-1]
    marcos["fim"] = {"ouro": fim["ouro_diff"], "xp": fim["xp_diff"], "cs": fim["cs_diff"]}

    return {
        "n_oponentes": len(op_pids),
        "serie": serie,
        "marcos": marcos,
        "pico_ouro": max(p["ouro_diff"] for p in serie),
        "vale_ouro": min(p["ouro_diff"] for p in serie),
    }


def linha_do_tempo_build(timeline: dict, puuid: str) -> dict:
    """
    Ordem e timing de COMPRA de itens e de subida de HABILIDADES do jogador, a partir
    dos eventos da timeline (ITEM_PURCHASED/SOLD/UNDO e SKILL_LEVEL_UP) — hoje
    ignorados por `normalizar_timeline`. ITEM_UNDO marca como 'desfeita' a última
    compra do item (beforeId). Devolve {itens:[{t_s,item_id,acao}], skills:[{t_s,slot}],
    ordem_max} com ordem_max = ordem de maximização das básicas (ex.: 'Q>E>W').
    """
    pid = _participant_id(timeline.get("metadata", {}).get("participants", []), puuid)
    frames = timeline.get("info", {}).get("frames", [])
    if pid is None:
        return {"itens": [], "skills": [], "ordem_max": ""}

    itens, skills = [], []
    for fr in frames:
        for ev in fr.get("events", []):
            if ev.get("participantId") != pid:
                continue
            tipo = ev.get("type")
            t_s = ev.get("timestamp", 0) // 1000
            if tipo == "ITEM_PURCHASED":
                itens.append({"t_s": t_s, "item_id": ev.get("itemId"), "acao": "compra"})
            elif tipo == "ITEM_SOLD":
                itens.append({"t_s": t_s, "item_id": ev.get("itemId"), "acao": "venda"})
            elif tipo == "ITEM_UNDO":
                alvo = ev.get("beforeId")
                for it in reversed(itens):
                    if it["acao"] == "compra" and it["item_id"] == alvo:
                        it["acao"] = "desfeita"
                        break
            elif tipo == "SKILL_LEVEL_UP" and ev.get("skillSlot") in _SLOT_LABEL:
                skills.append({"t_s": t_s, "slot": ev.get("skillSlot")})

    cont = {1: 0, 2: 0, 3: 0}
    for s in skills:
        if s["slot"] in cont:
            cont[s["slot"]] += 1
    ordem = sorted((k for k in cont if cont[k] > 0), key=lambda k: -cont[k])
    return {"itens": itens, "skills": skills,
            "ordem_max": ">".join(_SLOT_LABEL[k] for k in ordem)}


def dossie_partida(client: RiotClient, match_id: str, puuid: str, team_id: int) -> dict:
    """
    Dossiê de UMA partida para o agente analisar: estatísticas completas do jogador
    (challenges & cia., menos o dump cru e as runas, para não inchar o contexto)
    cruzadas com a timeline — cada morte com contexto e quem matou, locais
    recorrentes de morte, participação em objetivos e exposição no campo inimigo.
    A LEITURA QUALITATIVA (pontos fortes/fracos, erros repetidos, bons lances) é do
    LLM; aqui entregamos a EVIDÊNCIA estruturada.
    """
    match = obter_match(client, match_id)
    timeline = obter_timeline(client, match_id)
    dados = normalizar_timeline(timeline, puuid)
    perfil = _perfil_por_pid(match)
    pid_jogador = _participant_id(match.get("metadata", {}).get("participants", []), puuid)
    sua_rota = perfil.get(pid_jogador, {}).get("rota", "")
    grupo_jog = _grupo_rota(sua_rota)

    # Composições completas (as duas comps como um todo) por time.
    seu_time, inimigo = [], []
    for p in match.get("info", {}).get("participants", []):
        item = {"champ": p.get("championName", "?"),
                "rota": p.get("teamPosition") or p.get("individualPosition") or ""}
        (seu_time if p.get("teamId") == team_id else inimigo).append(item)
    confronto_de_lane = [c for c in inimigo if c["rota"] and _grupo_rota(c["rota"]) == grupo_jog]
    cacador_inimigo = next((c for c in inimigo if (c["rota"] or "").upper() == "JUNGLE"), None)

    def _hms(t_s):
        return f"{t_s // 60}:{t_s % 60:02d}"

    mortes = []
    for m in dados["mortes"]:
        ctx = contexto_morte(timeline, puuid, m)
        kp = perfil.get(m.get("killer_id"), {})
        mortes.append({
            "tempo": _hms(m["t_s"]),
            "fase": _fase_jogo(m["t_s"]),
            "morto_por": kp.get("champ", "execução/torre"),
            "morto_por_rota": kp.get("rota") or None,
            "era_oponente_de_lane": bool(kp.get("rota")) and _grupo_rota(kp.get("rota")) == grupo_jog,
            "assistencias_inimigas": len(m.get("assist_ids") or []),
            "isolado": ctx.get("isolado"),
            "desvantagem_numerica": ctx.get("outnumbered"),
            "deficit_ouro_vs_killer": ctx.get("deficit_ouro"),
            "regiao": _rotulo_regiao(m["x"], m["y"]) if m.get("x") is not None else None,
        })

    # Abates do jogador (para detectar roams, agressão e participação por fase).
    abates = [{"tempo": _hms(m["t_s"]), "fase": _fase_jogo(m["t_s"]),
               "vitima": perfil.get(m.get("victim_id"), {}).get("champ"),
               "vitima_rota": perfil.get(m.get("victim_id"), {}).get("rota") or None,
               "regiao": _rotulo_regiao(m["x"], m["y"]) if m.get("x") is not None else None}
              for m in dados["abates"]]

    epicos = [o for o in dados["objetivos"]
              if o["tipo"] in ("DRAGON", "BARON_NASHOR", "RIFTHERALD")]
    enr = enriquecer_objetivos(timeline, puuid, team_id, epicos)

    # Estatísticas ricas, enxutas (sem challenges_raw nem runas, que são enormes).
    ricos = extrair_dados_ricos(match, puuid)
    ricos.pop("challenges_raw", None)
    if "construcao" in ricos:
        ricos["construcao"].pop("runas", None)

    # Evolução de lane (só os marcos, não a série inteira) e ordem de build/skill.
    st_ = series_temporais(timeline, match, puuid, team_id)
    evolucao_lane = {"marcos": st_.get("marcos"), "pico_ouro": st_.get("pico_ouro"),
                     "vale_ouro": st_.get("vale_ouro")} if st_ else {}
    bld = linha_do_tempo_build(timeline, puuid)
    build = {
        "ordem_itens": [{"item_id": i["item_id"], "min": round(i["t_s"] / 60, 1)}
                        for i in bld["itens"] if i["acao"] == "compra"],
        "ordem_max_skill": bld["ordem_max"],
    }

    return {
        "sua_rota": sua_rota,
        "composicoes": {"seu_time": seu_time, "inimigo": inimigo},
        "confronto_de_lane": confronto_de_lane,
        "cacador_inimigo": cacador_inimigo,
        "estatisticas": ricos,
        "evolucao_lane": evolucao_lane,
        "build": build,
        "mortes": mortes,
        "abates": abates,
        "locais_recorrentes_de_morte": [c for c in clusterizar_mortes(dados["mortes"])
                                        if c["n"] >= 2],
        "objetivos_epicos": {
            "do_seu_time": sum(1 for o in enr if o["seu_time"]),
            "voce_participou": sum(1 for o in enr if o["seu_time"] and o.get("participou")),
            "detalhe": [{"tipo": o["tipo"], "seu_time": o["seu_time"],
                         "fase": _fase_jogo(o["t_s"]),
                         "voce_participou": o.get("participou"),
                         "tempo": _hms(o["t_s"]),
                         "sua_distancia": o.get("dist_jogador")} for o in enr],
        },
        "posicionamento": metricas_posicionamento(dados["trajetoria"], team_id),
    }
