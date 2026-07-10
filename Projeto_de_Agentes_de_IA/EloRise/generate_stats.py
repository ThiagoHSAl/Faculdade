from riot_client import RiotClient
from deteccao_rota import inferir_rotas_partida
import requests
import time
import concurrent.futures
from collections import Counter, defaultdict
from config import (BENCHMARKS_API_URL, ROLE_METRICS, ELO_METRICS, ELO_ORDER,
                    ROLE_LABELS, PLATFORM, REGION, FILA_PADRAO,
                    MATCH_COUNT, MIN_PARTIDAS_ROTA, LIMIAR_MONO_CAMPEAO,
                    MIN_JOGOS_RECORRENTE, MAX_POOL, MIN_AMOSTRA_CAMPEAO)


# Session com keep-alive para a API de benchmarks (mesma razão do RiotClient: evita
# um handshake TCP+TLS por chamada). Thread-safe para GETs concorrentes.
_HTTP = requests.Session()


def _get_json(url: str, params: dict = None, tentativas: int = 3) -> dict:
    """GET com retry e backoff em falhas de rede/HTTP (robustez das ferramentas do agente)."""
    ultimo_erro = None
    for i in range(tentativas):
        try:
            resposta = _HTTP.get(url, params=params, timeout=10)
            resposta.raise_for_status()
            return resposta.json()
        except requests.exceptions.RequestException as e:
            ultimo_erro = e
            time.sleep(0.6 * (i + 1))
    raise ultimo_erro


def carregar_benchmarks_rota(posicao: str, regiao: str = None, fila: str = FILA_PADRAO) -> dict:
    """
    Busca os benchmarks de uma rota em todos os elos na API de Benchmarks, para a `fila`.
    Retorna: { "ELO_DIVISAO": {"amostra", "kda", "cs_min", ...}, ... }

    Com `regiao` (ex.: "kr"), compara contra a mesma região; se não houver amostra
    suficiente nessa região, cai no benchmark global (fallback gracioso).
    """
    url = f"{BENCHMARKS_API_URL}/benchmarks/rota/{posicao.upper()}"
    if regiao:
        try:
            return _get_json(url, params={"regiao": regiao, "fila": fila})
        except requests.exceptions.RequestException:
            pass  # região sem dados suficientes → usa o benchmark global
    return _get_json(url, params={"fila": fila})


def carregar_benchmark_rota_elo(posicao: str, elo: str, regiao: str = None, fila: str = FILA_PADRAO) -> dict:
    """Benchmark médio de uma rota em um elo específico (ex.: BOTTOM, DIAMOND), para a `fila`.
    Com `regiao`, restringe à mesma região (com fallback para o global)."""
    url = f"{BENCHMARKS_API_URL}/benchmarks/rota/{posicao.upper()}/{elo.upper()}"
    if regiao:
        try:
            return _get_json(url, params={"regiao": regiao, "fila": fila})
        except requests.exceptions.RequestException:
            pass
    return _get_json(url, params={"fila": fila})


def carregar_benchmarks_campeoes(campeoes: list, posicao: str, regiao: str = None, fila: str = FILA_PADRAO) -> dict:
    """Busca o benchmark de uma rota restrito a um conjunto de campeões (mono = 1 nome,
    pool = vários) em todos os elos, para a `fila`. Mesma forma de `carregar_benchmarks_rota`:
    { "ELO_DIV": {"amostra", "kda", ...}, ... }. Em 404/erro/amostra fraca retorna {}
    (o chamador cai graciosamente no benchmark da rota inteira)."""
    if not campeoes:
        return {}
    url = f"{BENCHMARKS_API_URL}/benchmarks/campeoes/{posicao.upper()}"
    params = {"campeoes": ",".join(campeoes), "fila": fila}
    if regiao:
        params["regiao"] = regiao
    # Requisição direta (sem o retry/backoff de _get_json): um 404 aqui é um resultado
    # ESPERADO (amostra do campeão/pool < 20, ou backend ainda sem o endpoint) — não vale
    # gastar ~3.6s de retries; basta cair na média da rota.
    try:
        resp = _HTTP.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except requests.exceptions.RequestException:
        return {}


def extrair_metricas_participante(p: dict, duracao_min: float) -> dict:
    """
    Extrai as métricas de um participante de uma partida (match-v5), espelhando
    exatamente o cálculo do crawler (lol-api/crawler.py) para que os valores do
    jogador sejam comparáveis aos benchmarks agregados.
    """
    chal = p.get("challenges", {}) or {}
    cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
    kda = (p.get("kills", 0) + p.get("assists", 0)) / max(1, p.get("deaths", 0))

    return {
        # Base (por minuto)
        "kda": kda,
        "cs_min": cs / duracao_min,
        "ouro_min": p.get("goldEarned", 0) / duracao_min,
        "visao_min": p.get("visionScore", 0) / duracao_min,
        "dano_min": p.get("totalDamageDealtToChampions", 0) / duracao_min,
        # Macro / impacto (totais por partida)
        "dano_objetivos": p.get("damageDealtToObjectives", 0),
        "dano_torres": p.get("damageDealtToBuildings", 0),
        "tempo_cc": p.get("timeCCingOthers", 0),
        "pink_wards": p.get("visionWardsBoughtInGame", 0),
        "cura_total": p.get("totalHeal", 0),
        "dano_mitigado": p.get("damageSelfMitigated", 0),
        # Challenges
        "kpa": chal.get("killParticipation", 0),
        "solo_kills": chal.get("soloKills", 0),
        "cs_jungle_10m": chal.get("jungleCsBefore10Minutes", 0),
        "cs_rota_10m": chal.get("laneMinionsFirst10Minutes", 0),
        "pct_dano_time": chal.get("teamDamagePercentage", 0),
    }


def _resumo_participante_card(p: dict, duracao_min: float) -> dict:
    """Resumo de um participante para os cards de partida (estilo op.gg)."""
    cs = p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)
    k, d, a = p.get("kills", 0), p.get("deaths", 0), p.get("assists", 0)
    chal = p.get("challenges", {}) or {}
    return {
        "nick": p.get("riotIdGameName") or p.get("summonerName") or "?",
        "tag": p.get("riotIdTagline") or "",
        "champion": p.get("championName", ""),
        "champion_id": p.get("championId", 0),
        "lane": p.get("teamPosition", ""),
        "team_id": p.get("teamId", 0),
        "win": bool(p.get("win")),
        "kills": k, "deaths": d, "assists": a,
        "kda": round((k + a) / max(1, d), 2),
        "cs": cs,
        "cs_min": round(cs / duracao_min, 1) if duracao_min else 0,
        "ouro": p.get("goldEarned", 0),
        "dano": p.get("totalDamageDealtToChampions", 0),
        "dano_recebido": p.get("totalDamageTaken", 0),
        "wards": p.get("wardsPlaced", 0),
        "wards_mortas": p.get("wardsKilled", 0),
        "nivel": p.get("champLevel", 0),
        "itens": [p.get(f"item{i}", 0) for i in range(7)],
        "kp": round(chal.get("killParticipation", 0) * 100),
        "puuid": p.get("puuid", ""),
    }


def coletar_metricas_jogador(game_name: str, tag_line: str, count: int = MATCH_COUNT,
                             platform: str = None, region: str = None) -> dict:
    """
    Faz as chamadas à Riot API e devolve as MÉDIAS de todas as métricas do jogador,
    o elo oficial e a rota detectada (teamPosition mais frequente). Esta etapa é a
    cara (rede) — é o ponto natural de cache; trocar a rota não precisa repeti-la.

    `platform`/`region` definem o servidor (ex.: kr/asia); por padrão usa o de config.
    """
    platform = platform or PLATFORM
    region = region or REGION
    client = RiotClient(platform=platform, region=region)

    # 1. PUUID
    puuid = client.get_account(game_name, tag_line)["puuid"]

    # 2. Elo (ranked) e IDs de partida são independentes → buscar em paralelo
    #    (corta um round-trip, relevante em servidores distantes como o asia/KR).
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fut_ranked = ex.submit(client.get_ranked_entries, puuid)
        fut_ids = ex.submit(client.get_match_ids, puuid, count)
        ranked_data = fut_ranked.result()
        match_ids = fut_ids.result()

    elo_oficial = "UNRANKED"
    for entry in ranked_data:
        if entry["queueType"] == "RANKED_SOLO_5x5":
            elo_oficial = f"{entry['tier']}_{entry['rank']}"
            break

    # 3. Detalhe das partidas (em paralelo, com paralelismo limitado p/ respeitar o
    #    burst de 20 req/seg da chave grátis; o cliente já faz retry/sleep em 429).
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, max(1, len(match_ids)))) as executor:
        partidas_detalhadas = [
            m for m in executor.map(client.get_match, match_ids)
            if m["info"]["gameDuration"] >= 300
        ]

    # Cruza os sinais da match-v5 e deduz a rota REALMENTE jogada por cada um
    # (corrige o teamPosition deduplicado em casos de lane swap / autofill).
    # Calculada UMA vez por partida — o loop de métricas e o do histórico reusam.
    rotas_por_match = {
        m.get("metadata", {}).get("matchId", ""): inferir_rotas_partida(m["info"])
        for m in partidas_detalhadas
    }

    # 3. Acumula métricas por partida (com a ROTA de cada uma) e conta a posição jogada.
    acumulado = defaultdict(float)
    contagem_posicao = Counter()
    partidas_validas = 0
    partidas_descartadas = 0  # rota indeduzível (swap/autofill ambíguo) → fora da métrica
    partidas_metricas = []  # por partida: {posicao, metricas, duracao_min} → agregação por rota

    for match_data in partidas_detalhadas:
        info = match_data["info"]
        duracao_min = info["gameDuration"] / 60.0
        rotas_inferidas = rotas_por_match[match_data.get("metadata", {}).get("matchId", "")]

        for participant in info["participants"]:
            if participant["puuid"] == puuid:
                inf = rotas_inferidas.get(puuid, {})
                # Descartar é o ÚLTIMO caso: só quando os sinais não convergem o
                # bastante pra deduzir a rota com segurança (incluí-la poluiria a métrica).
                if not inf.get("confiavel"):
                    partidas_descartadas += 1
                    break

                posicao = inf["rota"]
                metricas = extrair_metricas_participante(participant, duracao_min)
                for chave, valor in metricas.items():
                    acumulado[chave] += valor

                contagem_posicao[posicao] += 1
                partidas_metricas.append({
                    "posicao": posicao,
                    "champion": participant.get("championName", ""),
                    "metricas": metricas,
                    "duracao_min": duracao_min,
                    "match_id": match_data.get("metadata", {}).get("matchId", ""),
                })
                partidas_validas += 1
                break

    if partidas_validas == 0:
        raise Exception("Nenhuma partida válida encontrada.")

    medias = {chave: valor / partidas_validas for chave, valor in acumulado.items()}
    posicao_detectada = contagem_posicao.most_common(1)[0][0] if contagem_posicao else "MIDDLE"

    # 4. Histórico de partidas (cards estilo op.gg) a partir das mesmas partidas
    historico = []
    for match_data in partidas_detalhadas:
        info = match_data["info"]
        duracao_min = info["gameDuration"] / 60.0
        rotas_inferidas = rotas_por_match[match_data.get("metadata", {}).get("matchId", "")]
        participantes = [_resumo_participante_card(p, duracao_min) for p in info["participants"]]
        for pc in participantes:  # mostra a rota deduzida (não o teamPosition cru)
            inf = rotas_inferidas.get(pc["puuid"])
            if inf:
                pc["lane"] = inf["rota"]
        jogador = next((p for p in participantes if p["puuid"] == puuid), None)
        historico.append({
            "match_id": match_data.get("metadata", {}).get("matchId", ""),
            "fila": info.get("gameMode", ""),
            "fim_ts": info.get("gameEndTimestamp") or info.get("gameCreation", 0),
            "duracao_seg": int(info["gameDuration"]),
            "venceu": bool(jogador["win"]) if jogador else False,
            "jogador": jogador,
            "participantes": participantes,
        })

    return {
        "nick": f"{game_name}#{tag_line}",
        "puuid": puuid,  # checagem barata do monitor (1 chamada) sem re-resolver a conta
        "elo_oficial": elo_oficial,
        "regiao": platform,  # filtro de região dos benchmarks (= código de plataforma)
        "posicao_detectada": posicao_detectada,
        "metricas_brutas": medias,                  # média global (compat); diagnóstico usa por rota
        "partidas_metricas": partidas_metricas,     # por partida + rota → agregação por rota
        "partidas_analisadas": partidas_validas,
        "partidas_descartadas": partidas_descartadas,  # rota indeduzível → fora do agregado
        "historico": historico,
    }


def _calcular_diff(valor_jogador: float, valor_meta: float) -> dict:
    if not valor_meta:  # benchmark ausente/zerado → não dá para comparar
        return {
            "valor_jogador": round(valor_jogador, 2),
            "valor_meta": round(valor_meta, 2),
            "diff_pct": 0.0,
            "status": "N/D",
        }
    diff = ((valor_jogador - valor_meta) / valor_meta) * 100
    return {
        "valor_jogador": round(valor_jogador, 2),
        "valor_meta": round(valor_meta, 2),
        "diff_pct": round(diff, 1),
        "status": "ACIMA" if diff >= 0 else "ABAIXO",
    }


_PONTOS_PERCENTIS = list(range(5, 100, 5))  # grade p5..p95 servida pela API


def _percentil_na_grade(valor: float, grade: list | None) -> int | None:
    """Percentil aproximado de `valor` na grade p5..p95 (interpolação linear entre
    pontos). Fora da grade satura em 5/95 — com 19 pontos não dá para afirmar mais
    que "top 5%" sem inventar precisão."""
    if not grade or len(grade) != len(_PONTOS_PERCENTIS):
        return None
    if valor <= grade[0]:
        return _PONTOS_PERCENTIS[0]
    for i in range(1, len(grade)):
        if valor <= grade[i]:
            g0, g1 = grade[i - 1], grade[i]
            fracao = (valor - g0) / (g1 - g0) if g1 > g0 else 1.0
            return round(_PONTOS_PERCENTIS[i - 1] + fracao * 5)
    return _PONTOS_PERCENTIS[-1]


def agregar_metricas_rota(partidas_metricas: list, posicao: str) -> tuple[dict, int]:
    """Média das métricas APENAS nas partidas jogadas na rota informada (não mistura
    funções). Retorna (medias, n_partidas_na_rota)."""
    posicao = (posicao or "").upper()
    rota = [p for p in (partidas_metricas or []) if (p.get("posicao") or "").upper() == posicao]
    if not rota:
        return {}, 0
    soma = defaultdict(float)
    for p in rota:
        for chave, valor in p.get("metricas", {}).items():
            soma[chave] += valor
    n = len(rota)
    return {chave: valor / n for chave, valor in soma.items()}, n


def agregar_metricas_rota_periodo(dados_brutos: dict, posicao: str,
                                  apos_ts: int = None) -> tuple[dict, int]:
    """Como agregar_metricas_rota, mas só com as partidas da rota cujo fim_ts > `apos_ts`
    (passo 7 — 'partidas após o plano'). As entradas de `partidas_metricas` só têm match_id,
    então cruzamos com `historico` (que tem fim_ts) por match_id para obter o tempo de cada
    partida. Sem `apos_ts`, agrega todas as da rota. Retorna (medias, n_partidas)."""
    partidas = dados_brutos.get("partidas_metricas", [])
    if apos_ts:
        ts_por_match = {
            h.get("match_id"): h.get("fim_ts", 0)
            for h in dados_brutos.get("historico", [])
        }
        partidas = [p for p in partidas
                    if ts_por_match.get(p.get("match_id"), 0) > apos_ts]
    return agregar_metricas_rota(partidas, posicao)


def escolher_base_comparacao(partidas_metricas: list, posicao: str) -> dict:
    """Decide contra QUEM comparar o jogador na rota, conforme seu repertório:
      - 'mono': 1 campeão domina (>= LIMIAR_MONO_CAMPEAO das partidas da rota) OU só há
                1 campeão recorrente → compara contra esse campeão;
      - 'pool': 2..MAX_POOL campeões recorrentes → compara contra a média só deles;
      - 'rota': repertório espalhado (mais recorrentes que MAX_POOL) ou sem campeão
                identificável → média da rota inteira (comportamento antigo).
    'Recorrente' = >= MIN_JOGOS_RECORRENTE partidas na rota. Retorna
    {'tipo', 'campeoes'} — 'campeoes' vazio quando 'rota'."""
    posicao = (posicao or "").upper()
    jogos = Counter(
        (p.get("champion") or "").strip()
        for p in (partidas_metricas or [])
        if (p.get("posicao") or "").upper() == posicao and (p.get("champion") or "").strip()
    )
    total = sum(jogos.values())
    if not total:
        return {"tipo": "rota", "campeoes": []}

    champ_top, jogos_top = jogos.most_common(1)[0]
    recorrentes = [c for c, n in jogos.items() if n >= MIN_JOGOS_RECORRENTE]

    if (jogos_top / total) >= LIMIAR_MONO_CAMPEAO or len(recorrentes) == 1:
        return {"tipo": "mono", "campeoes": [champ_top]}
    if 2 <= len(recorrentes) <= MAX_POOL:
        return {"tipo": "pool", "campeoes": sorted(recorrentes)}
    return {"tipo": "rota", "campeoes": []}


def montar_diagnostico(dados_brutos: dict, posicao: str, benchmarks_rota: dict = None) -> dict:
    """
    Monta o perfil de diagnóstico para uma rota específica, usando apenas as
    métricas relevantes dela (ROLE_METRICS) e SÓ as partidas daquela rota. Etapa
    barata: pode ser recalculada ao trocar a rota sem refazer as chamadas à Riot.
    Se houver menos de MIN_PARTIDAS_ROTA partidas na rota, marca amostra insuficiente.
    """
    posicao = posicao.upper()
    if posicao not in ROLE_METRICS:
        posicao = "MIDDLE"
    metricas_rota = ROLE_METRICS[posicao]

    # Agrega SÓ as partidas da rota selecionada (apples-to-apples com o benchmark da rota).
    medias, n_rota = agregar_metricas_rota(dados_brutos.get("partidas_metricas", []), posicao)
    elo_oficial = dados_brutos["elo_oficial"]

    # Amostra insuficiente na rota → não dá pra comparar as métricas com segurança.
    if n_rota < MIN_PARTIDAS_ROTA:
        return {
            "nick": dados_brutos["nick"],
            "elo_oficial": elo_oficial,
            "regiao": dados_brutos.get("regiao"),
            "posicao": posicao,
            "posicao_label": ROLE_LABELS.get(posicao, posicao),
            "amostra_insuficiente": True,
            "partidas_rota": n_rota,
            "minimo_partidas": MIN_PARTIDAS_ROTA,
            "metricas": {},
            "pior_metrica_identificada": None,
            "partidas_analisadas": n_rota,
            "elo_comparacao": elo_oficial,
            "elo_equivalente": elo_oficial.replace("_", " "),
            "percentil_geral": None,
            "elo_percentil": elo_oficial,
        }

    if benchmarks_rota is None:
        benchmarks_rota = carregar_benchmarks_rota(posicao, dados_brutos.get("regiao"))

    if not benchmarks_rota:
        raise Exception(f"Sem benchmarks disponíveis para a rota {posicao}.")

    # Base de comparação consciente do campeão: mono (vs o próprio campeão), pool
    # (vs a média dos campeões recorrentes) ou rota (média da rota inteira). Só troca
    # da rota para campeão/pool se o benchmark do DB tiver o elo oficial com amostra
    # suficiente; senão degrada graciosamente para a rota.
    benchmarks = benchmarks_rota
    base_comparacao = "rota"
    campeoes_referencia: list = []
    amostra_referencia = None
    escolha_base = escolher_base_comparacao(dados_brutos.get("partidas_metricas", []), posicao)
    if escolha_base["tipo"] != "rota":
        bench_camp = carregar_benchmarks_campeoes(
            escolha_base["campeoes"], posicao, dados_brutos.get("regiao")
        )
        bloco_elo = bench_camp.get(elo_oficial)
        if bloco_elo and bloco_elo.get("amostra", 0) >= MIN_AMOSTRA_CAMPEAO:
            benchmarks = bench_camp
            base_comparacao = escolha_base["tipo"]
            campeoes_referencia = escolha_base["campeoes"]
            amostra_referencia = bloco_elo.get("amostra")

    # Benchmark do elo alvo (oficial, com fallback)
    if elo_oficial in benchmarks:
        elo_alvo = elo_oficial
    elif "SILVER_IV" in benchmarks:
        elo_alvo = "SILVER_IV"
    else:
        elo_alvo = next(iter(benchmarks))
    meta = benchmarks[elo_alvo]

    # Elo equivalente: usa SÓ as métricas que crescem monotonicamente com o elo
    # (ELO_METRICS, validadas contra o cache global de benchmarks) e um escore
    # COM SINAL por elo — média de clamp((jogador - ref) / ref, ±0.6). Positivo
    # significa "jogador acima da média daquele elo"; o equivalente é o elo MAIS
    # ALTO com escore ≥ 0. Por construção é monotônico: melhorar qualquer métrica
    # nunca rebaixa a estimativa (a distância absoluta antiga tratava "acima da
    # média" como desencaixe e casava com elos baixos quando o jogador melhorava).
    # Compara sempre com o benchmark da ROTA (31 sub-elos, amostra grande) — os
    # benchmarks por campeão têm amostra rala fora do elo oficial.
    LIMITE_METRICA = 0.6  # contribuição máxima por métrica (±60%)
    metricas_elo = ELO_METRICS.get(posicao, metricas_rota)

    def escore_do_elo(dados_elo: dict) -> float | None:
        desvios = []
        for m in metricas_elo:
            ref = dados_elo.get(m, 0)
            if not ref:  # sem benchmark → ignora (evita divisão por zero)
                continue
            desvio = (medias.get(m, 0) - ref) / ref
            desvios.append(max(-LIMITE_METRICA, min(desvio, LIMITE_METRICA)))
        return sum(desvios) / len(desvios) if desvios else None

    elo_equivalente = elo_oficial
    escores = {e: s for e in ELO_ORDER if e in benchmarks_rota
               and (s := escore_do_elo(benchmarks_rota[e])) is not None}
    if escores:
        acima_da_media = [e for e, s in escores.items() if s >= 0]
        # Acima da média de algum elo → o mais alto deles; abaixo de todos → o menor.
        elo_equivalente = acima_da_media[-1] if acima_da_media else next(iter(escores))

    # Diffs por métrica da rota
    metricas = {m: _calcular_diff(medias.get(m, 0), meta.get(m, 0)) for m in metricas_rota}

    # Percentil dentro do elo OFICIAL, contra a rota inteira: "melhor que X% das
    # partidas de {elo} nesta rota". É a leitura que a amostra sustenta — as médias
    # de elos vizinhos se sobrepõem demais para um rótulo de sub-elo confiável.
    # A grade p5..p95 vem do cache diário do servidor (bloco 'percentis' da API);
    # se o servidor ainda não a expõe, os campos ficam None e a UI omite.
    elo_percentil = elo_oficial if elo_oficial in benchmarks_rota else (
        "SILVER_IV" if "SILVER_IV" in benchmarks_rota else next(iter(benchmarks_rota)))
    grades = benchmarks_rota[elo_percentil].get("percentis") or {}
    for m in metricas_rota:
        metricas[m]["percentil_elo"] = _percentil_na_grade(medias.get(m, 0), grades.get(m))
    # Resumo (linha de destaque da UI): mediana dos percentis das métricas que
    # crescem com o elo (ELO_METRICS) — as mesmas que separam os elos de verdade.
    percentis_resumo = sorted(
        p for m in metricas_elo
        if (p := _percentil_na_grade(medias.get(m, 0), grades.get(m))) is not None
    )
    percentil_geral = (percentis_resumo[len(percentis_resumo) // 2]
                       if percentis_resumo else None)

    # Pior métrica = menor diff_pct entre as comparáveis
    comparaveis = {m: d for m, d in metricas.items() if d["status"] != "N/D"}
    pior_metrica = (
        min(comparaveis.items(), key=lambda x: x[1]["diff_pct"])[0]
        if comparaveis else metricas_rota[0]
    )

    return {
        "nick": dados_brutos["nick"],
        "elo_oficial": elo_oficial,
        "regiao": dados_brutos.get("regiao"),  # região comparada (= código de plataforma)
        "elo_comparacao": elo_alvo,  # elo cujo benchmark é a base do "vs Meta"
        "elo_equivalente": elo_equivalente.replace("_", " "),
        "posicao": posicao,
        "posicao_label": ROLE_LABELS.get(posicao, posicao),
        "metricas": metricas,
        "pior_metrica_identificada": pior_metrica,
        "amostra_insuficiente": False,
        "partidas_rota": n_rota,
        "partidas_analisadas": n_rota,  # específico da rota (não a média global)
        # Percentis vs o elo oficial (rota inteira, distribuição global de partidas)
        "percentil_geral": percentil_geral,   # mediana das ELO_METRICS (None sem grade)
        "elo_percentil": elo_percentil,        # elo cuja distribuição foi a referência
        # Base de comparação: "mono" | "pool" | "rota" (consciente do campeão)
        "base_comparacao": base_comparacao,
        "campeoes_referencia": campeoes_referencia,
        "amostra_referencia": amostra_referencia,
        # Benchmark efetivamente usado (campeão/pool/rota) → o plano usa o mesmo p/ alvo
        "benchmarks_base": benchmarks,
    }


def gerar_diagnostico_jogador(game_name: str, tag_line: str, posicao: str = None) -> dict:
    """
    Orquestra coleta + diagnóstico. `posicao=None` usa a rota detectada.
    Mantida para uso direto/standalone (a UI usa coletar + montar separadamente
    para cachear a coleta e permitir troca de rota barata).
    """
    dados = coletar_metricas_jogador(game_name, tag_line)
    posicao = posicao or dados["posicao_detectada"]
    return montar_diagnostico(dados, posicao)
