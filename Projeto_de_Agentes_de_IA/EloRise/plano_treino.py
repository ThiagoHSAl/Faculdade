"""
plano_treino.py — Objetivo + plano de treino estruturado (passo 4 do roadmap de agente).

Transforma o diagnóstico do jogador (pior métrica) em uma META CONCRETA e VERIFICÁVEL:
subir a métrica deficitária do valor atual até o benchmark da MESMA métrica no
PRÓXIMO ELO ACIMA, com um checklist de drills práticos. O objeto retornado é puro
(dict serializável em JSON) para viver no State do grafo e ser persistido por jogador.
"""
import random
from datetime import date, datetime

from config import ELO_ORDER, METRIC_LABELS
from base_conhecimento import drills_da_metrica, tags_do_jogador, DRILLS_GENERICO


def _drill_aplicavel(drill: dict, tags_jogador: set) -> bool:
    """Um drill serve ao jogador se NÃO exige arquétipo (`requer` vazio = universal) ou se
    ao menos uma das etiquetas exigidas casa com o arquétipo do jogador (rota/classe/
    arquétipo refinado). Drills específicos de outras funções ficam de fora."""
    requer = set(drill.get("requer") or [])
    return not requer or bool(requer & tags_jogador)


def _selecionar_drills(metrica: str, evitar_metas=None, n: int = 3,
                       tags_jogador: set = None) -> list[dict]:
    """Sorteia `n` drills da métrica RELEVANTES ao arquétipo do jogador (`tags_jogador`),
    evitando repetir um mesmo `tema` no mesmo plano e priorizando metas ainda não usadas
    (`evitar_metas`) — assim REGENERAR traz drills diferentes. Se a filtragem deixar
    candidatos de menos, completa com os genéricos universais (nunca com drills de
    outra função)."""
    tags_jogador = set(tags_jogador or [])
    evitar = set(evitar_metas or [])
    pool = list(drills_da_metrica(metrica))

    # 1) só drills que servem ao arquétipo; se sobrar pouco, completa com os drills
    #    GENÉRICOS universais — NUNCA ressuscita drill de outra função (ex.: exercício
    #    de Arauto para um ADC; feedback de usuário).
    aplicaveis = [d for d in pool if _drill_aplicavel(d, tags_jogador)]
    if len(aplicaveis) < n:
        aplicaveis = aplicaveis + [d for d in DRILLS_GENERICO if d not in aplicaveis]
    # 2) prioriza metas inéditas; completa com as já usadas se faltar.
    frescos = [d for d in aplicaveis if d["meta"] not in evitar]
    candidatos = frescos if len(frescos) >= n else aplicaveis
    random.shuffle(candidatos)

    # 3) escolhe evitando repetir o mesmo tema no plano; completa se a dedupe faltar.
    escolhidos, temas = [], set()
    for d in candidatos:
        tema = d.get("tema")
        if tema and tema in temas:
            continue
        escolhidos.append(d)
        if tema:
            temas.add(tema)
        if len(escolhidos) == n:
            return escolhidos
    for d in candidatos:
        if d not in escolhidos:
            escolhidos.append(d)
            if len(escolhidos) == n:
                break
    return escolhidos[:n]


def ranking_metricas(perfil: dict) -> list[str]:
    """Ordena as métricas COMPARÁVEIS da rota da mais fraca para a mais forte (menor
    diff_pct primeiro). Base para escolher qual métrica o plano vai atacar a seguir."""
    comparaveis = {
        m: d for m, d in (perfil.get("metricas") or {}).items()
        if d.get("status") != "N/D"
    }
    return sorted(comparaveis, key=lambda m: comparaveis[m]["diff_pct"])


def proxima_metrica(perfil: dict, superadas=None) -> str | None:
    """Métrica-alvo do próximo plano: a mais fraca que AINDA não foi superada. Quando o
    jogador atinge a meta de uma métrica e gera um novo plano, ela entra em `superadas` e
    o foco passa para a próxima mais fraca. Se todas já foram superadas, recomeça pela
    mais fraca (novo ciclo). Retorna None se não houver métrica comparável."""
    ranking = ranking_metricas(perfil)
    if not ranking:
        return perfil.get("pior_metrica_identificada")
    superadas = set(superadas or [])
    for metrica in ranking:
        if metrica not in superadas:
            return metrica
    return ranking[0]  # todas superadas → reinicia o ciclo pela mais fraca


def avancar_metrica(perfil: dict, metrica_atual: str, superadas=None) -> str | None:
    """Próxima métrica ao gerar um NOVO plano: anda no ranking (mais fraca → mais forte)
    a partir da atual, ciclando. Pula a métrica atual e as já dominadas; se todas as outras
    estiverem dominadas, segue mesmo assim para a próxima do ciclo (não trava na mesma)."""
    ranking = ranking_metricas(perfil)
    if not ranking:
        return perfil.get("pior_metrica_identificada")
    superadas = set(superadas or [])
    # ordem começando LOGO APÓS a métrica atual, ciclando até voltar nela.
    if metrica_atual in ranking:
        i = ranking.index(metrica_atual)
        ordem = ranking[i + 1:] + ranking[:i + 1]
    else:
        ordem = ranking
    for m in ordem:                       # 1ª diferente da atual e ainda não dominada
        if m != metrica_atual and m not in superadas:
            return m
    for m in ordem:                       # todas dominadas → próxima do ciclo mesmo assim
        if m != metrica_atual:
            return m
    return metrica_atual                  # só existe 1 métrica comparável


def _proximo_elo_com_benchmark(elo_base: str, benchmarks_rota: dict) -> str | None:
    """Retorna a primeira chave de elo ACIMA de `elo_base` (em ELO_ORDER) que exista
    em `benchmarks_rota`. Se não houver elo acima com dados, devolve o mais alto
    disponível; se nem o elo_base existir na ordem, devolve None."""
    if elo_base not in ELO_ORDER:
        return None
    idx = ELO_ORDER.index(elo_base)
    # Procura para cima a partir do elo seguinte
    for nome in ELO_ORDER[idx + 1:]:
        if nome in benchmarks_rota:
            return nome
    # Sem elo acima com dados: usa o elo disponível mais alto (pode ser o próprio base)
    disponiveis = [e for e in ELO_ORDER if e in benchmarks_rota]
    return disponiveis[-1] if disponiveis else None


def gerar_plano_treino(perfil: dict, benchmarks_rota: dict, baseline_fim_ts: int = None,
                       evitar_metas=None, n_drills: int = 3, metrica_alvo: str = None) -> dict:
    """Monta a meta concreta a partir de uma métrica deficitária:
    valor atual → benchmark da mesma métrica no próximo elo acima + checklist de drills.
    `baseline_fim_ts` = timestamp da partida mais recente na criação (passo 5: serve de
    marco para contar quantas partidas novas foram jogadas desde que a meta foi traçada).
    `evitar_metas` = metas (descrições) já usadas a evitar, para que regenerar o plano da
    mesma métrica traga drills diferentes.
    `metrica_alvo` = métrica a atacar; se None, usa a pior métrica do diagnóstico. Permite
    avançar para a próxima métrica mais fraca depois de uma meta atingida."""
    metrica = metrica_alvo or perfil["pior_metrica_identificada"]
    dados_metrica = perfil["metricas"].get(metrica, {})
    valor_inicial = float(dados_metrica.get("valor_jogador", 0) or 0)
    elo_base = perfil["elo_oficial"]

    elo_alvo = _proximo_elo_com_benchmark(elo_base, benchmarks_rota)
    valor_alvo = None
    if elo_alvo and metrica in benchmarks_rota.get(elo_alvo, {}):
        valor_alvo = float(benchmarks_rota[elo_alvo][metrica] or 0)

    # Fallback de alvo: métrica ausente/zerada no elo de cima → 10% acima da média do
    # elo atual (ou do próprio valor inicial), sinalizando "manter/superar o topo".
    if not valor_alvo:
        base = float(dados_metrica.get("valor_meta", 0) or 0) or valor_inicial
        valor_alvo = round(base * 1.10, 2)
        elo_alvo = elo_alvo or elo_base

    # Cada passo é uma META com sub-metas. A meta principal conclui sozinha quando todas
    # as sub-metas são marcadas (ver marcar_submeta/_sincronizar_passo). Sorteamos um
    # subconjunto do banco (evitando as metas anteriores) para variar a cada regeneração.
    tags_jogador = tags_do_jogador(perfil)
    passos = [
        {
            "descricao": d["meta"],
            "concluido": False,
            "submetas": [{"descricao": s, "concluido": False} for s in d.get("submetas", [])],
        }
        for d in _selecionar_drills(metrica, evitar_metas, n_drills, tags_jogador)
    ]

    return {
        # Identidade estável do plano (para histórico/restauração e chaves de UI únicas).
        "id": datetime.now().isoformat(),
        "drills_versao": 0,  # incrementa a cada "trocar exercícios" (renova as chaves dos checkboxes)
        "metrica": metrica,
        "metrica_label": METRIC_LABELS.get(metrica, metrica.upper().replace("_", " ")),
        "posicao": perfil["posicao"],
        # Base de comparação herdada do diagnóstico: alvo e cobrança seguem a mesma
        # referência (mono = vs o próprio campeão; pool = vs a pool; rota = média geral).
        "base_comparacao": perfil.get("base_comparacao", "rota"),
        "campeoes_referencia": perfil.get("campeoes_referencia", []),
        "elo_base": elo_base,
        "elo_alvo": elo_alvo,
        "valor_inicial": round(valor_inicial, 2),
        "valor_alvo": round(valor_alvo, 2),
        "valor_atual": round(valor_inicial, 2),
        "criado_em": date.today().isoformat(),
        # Foto de TODAS as métricas da rota no momento em que o plano foi aberto (passo 7):
        # serve de "antes" para a aba de Evolução comparar com as partidas jogadas depois.
        # O plano foca em uma métrica, mas acompanhamos a mudança de todas.
        "metricas_baseline": {
            m: {"valor": d.get("valor_jogador"), "meta": d.get("valor_meta")}
            for m, d in (perfil.get("metricas") or {}).items()
        },
        "elo_comparacao": perfil.get("elo_comparacao", elo_base),
        "passos": passos,
        "baseline_fim_ts": baseline_fim_ts,  # marco p/ contar partidas novas (passo 5)
        "ultimo_fim_ts_visto": baseline_fim_ts,  # mais recente já contabilizado (passo 6)
        "ultima_verificacao": datetime.now().isoformat(),  # throttle do monitor (passo 6)
        "medicoes": [],                       # histórico de reavaliações (passo 5)
        "concluido": False,                   # True quando valor_atual >= valor_alvo
    }


def assinatura_plano(plano: dict) -> str:
    """Identidade estável de um plano, para deduplicar/identificar no histórico."""
    if not plano:
        return ""
    return str(plano.get("id") or f"{plano.get('criado_em')}|{plano.get('metrica')}")


def trocar_drills(plano: dict, n_drills: int = 3) -> dict:
    """Sorteia OUTROS exercícios para a MESMA métrica, preservando TODO o resto do plano
    (métrica-alvo, valores, baseline, medições e métricas_baseline) — troca os drills sem
    perder o histórico de evolução. Evita repetir os drills atuais e renova `drills_versao`
    (para a UI recriar os checkboxes zerados em vez de herdar marcações antigas)."""
    if not plano:
        return plano
    evitar = [p["descricao"] for p in plano.get("passos", [])]
    tags = tags_do_jogador(plano)  # o plano carrega posicao + campeoes_referencia
    plano["passos"] = [
        {
            "descricao": d["meta"],
            "concluido": False,
            "submetas": [{"descricao": s, "concluido": False} for s in d.get("submetas", [])],
        }
        for d in _selecionar_drills(plano["metrica"], evitar, n_drills, tags)
    ]
    plano["drills_versao"] = int(plano.get("drills_versao", 0)) + 1
    return plano


def atualizar_valor_atual(plano: dict, perfil: dict) -> dict:
    """Recalcula `valor_atual` da métrica-alvo a partir de um diagnóstico atualizado
    (gancho do passo 5: medir se a métrica melhorou). Retorna o próprio plano."""
    if not plano:
        return plano
    dados = perfil.get("metricas", {}).get(plano["metrica"])
    if dados and dados.get("valor_jogador") is not None:
        plano["valor_atual"] = round(float(dados["valor_jogador"]), 2)
    return plano


def descrever_base_plano(plano: dict) -> str:
    """Texto curto de contra quem o alvo do plano é medido (mono/pool/rota)."""
    base = (plano or {}).get("base_comparacao", "rota")
    champs = (plano or {}).get("campeoes_referencia") or []
    if base == "mono" and champs:
        return f"referência: outros jogadores de {champs[0]}"
    if base == "pool" and champs:
        return f"referência: sua pool ({', '.join(champs)})"
    return "referência: média geral da rota"


def progresso_metrica(plano: dict) -> float:
    """Fração 0..1 do caminho percorrido entre valor_inicial e valor_alvo."""
    if not plano:
        return 0.0
    inicial = plano.get("valor_inicial", 0)
    alvo = plano.get("valor_alvo", 0)
    atual = plano.get("valor_atual", inicial)
    if alvo == inicial:
        return 1.0 if atual >= alvo else 0.0
    frac = (atual - inicial) / (alvo - inicial)
    return max(0.0, min(1.0, frac))


def meta_atingida(plano: dict) -> bool:
    """Métricas de ROLE_METRICS são todas 'maior = melhor' → meta = atingir o alvo."""
    if not plano:
        return False
    return plano.get("valor_atual", 0) >= plano.get("valor_alvo", 0)


def registrar_medicao(plano: dict, valor_atual: float, partidas_novas: int) -> dict:
    """Passo 5: registra uma reavaliação. Atualiza o valor atual da métrica-alvo,
    guarda a medição na tendência e marca o plano como concluído se cruzou o alvo."""
    if not plano:
        return plano
    plano["valor_atual"] = round(float(valor_atual), 2)
    plano.setdefault("medicoes", []).append({
        "data": date.today().isoformat(),
        "valor": plano["valor_atual"],
        "partidas_novas": int(partidas_novas),
    })
    plano["concluido"] = meta_atingida(plano)
    return plano


def resumo_progresso(plano: dict) -> str:
    """Texto do progresso para a ferramenta do agente (verificar_progresso)."""
    if not plano:
        return ("Ainda não há um plano de treino para acompanhar. Sugira que o jogador "
                "gere um na aba 'Plano de Treino'.")
    pct = round(progresso_metrica(plano) * 100)
    novas = sum(m.get("partidas_novas", 0) for m in plano.get("medicoes", []))
    linhas = [
        f"PROGRESSO DA META ({plano['metrica_label']}, {plano['posicao']}):",
        f"- Trajetória: {plano['valor_inicial']} (início) → {plano['valor_atual']} (atual) "
        f"→ {plano['valor_alvo']} (alvo). {pct}% do caminho.",
        f"- Reavaliações feitas: {len(plano.get('medicoes', []))}"
        + (f" (em {novas} partidas novas desde a meta)." if novas else "."),
    ]
    if meta_atingida(plano):
        linhas.append("- META ATINGIDA! Parabenize o jogador e sugira traçar uma nova "
                      "meta para a próxima métrica mais fraca.")
    else:
        falta = round(plano["valor_alvo"] - plano["valor_atual"], 2)
        linhas.append(f"- Falta {falta} para o alvo. Incentive a continuar os passos do plano.")
    return "\n".join(linhas)


def _sincronizar_passo(passo: dict) -> None:
    """Se o passo tem sub-metas, a meta principal conclui sozinha quando TODAS estão
    marcadas (e desmarca se alguma sub-meta for desmarcada)."""
    subs = passo.get("submetas")
    if subs:
        passo["concluido"] = all(s.get("concluido") for s in subs)


def marcar_passo(plano: dict, indice: int, concluido: bool = True) -> dict:
    """Marca/desmarca um passo do checklist pelo índice (0-based). Passos COM sub-metas são
    derivados das sub-metas (use marcar_submeta); marcar direto só vale para passos simples
    (planos antigos sem sub-metas)."""
    if plano and 0 <= indice < len(plano.get("passos", [])):
        passo = plano["passos"][indice]
        if not passo.get("submetas"):
            passo["concluido"] = bool(concluido)
    return plano


def marcar_submeta(plano: dict, i_passo: int, i_sub: int, concluido: bool = True) -> dict:
    """Marca/desmarca uma sub-meta (i_sub) de um passo (i_passo) e re-sincroniza a meta
    principal (que conclui sozinha quando todas as sub-metas estão marcadas)."""
    passos = (plano or {}).get("passos", [])
    if plano and 0 <= i_passo < len(passos):
        subs = passos[i_passo].get("submetas") or []
        if 0 <= i_sub < len(subs):
            subs[i_sub]["concluido"] = bool(concluido)
            _sincronizar_passo(passos[i_passo])
    return plano


def formatar_plano(plano: dict) -> str:
    """Texto do plano para a ferramenta do agente (consultar_plano)."""
    if not plano:
        return ("Ainda não há um plano de treino definido para este jogador. "
                "Sugira que ele gere um na aba 'Plano de Treino'.")
    elo_base = plano["elo_base"].replace("_", " ")
    elo_alvo = plano["elo_alvo"].replace("_", " ")
    feitos = sum(1 for p in plano["passos"] if p["concluido"])
    linhas = [
        f"META DE TREINO ({plano['posicao']}):",
        f"- Métrica-alvo: {plano['metrica_label']}",
        f"- Base de comparação: {descrever_base_plano(plano)}.",
        f"- Objetivo: subir de {plano['valor_inicial']} para {plano['valor_alvo']} "
        f"(referência do elo {elo_alvo}, acima do atual {elo_base}).",
        f"- Valor atual: {plano['valor_atual']}.",
        f"- Passos concluídos: {feitos}/{len(plano['passos'])}.",
        "Passos do plano:",
    ]
    for i, p in enumerate(plano["passos"], 1):
        marca = "[x]" if p["concluido"] else "[ ]"
        linhas.append(f"  {marca} {i}. {p['descricao']}")
        for s in p.get("submetas", []):
            sub_marca = "[x]" if s.get("concluido") else "[ ]"
            linhas.append(f"      {sub_marca} {s['descricao']}")
    return "\n".join(linhas)
