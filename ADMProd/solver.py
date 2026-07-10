# -*- coding: utf-8 -*-
"""
Modelo de Otimizacao da Cadeia de Suprimentos de Cafe (MILP).

Fiel as equacoes (1)-(13) do enunciado, estendido com:
  - variaveis inteiras de numero de viagens (n_ik, n_kj) e capacidade do caminhao
  - filtro de arcos por limite de emissao de CO2

Premissas (nao fornecidas pelo enunciado, documentadas no relatorio):
  - distancia: haversine(lat,lon) em km
  - custo de transporte: R$ 1,00 por km percorrido por viagem (caminhao)
  - fator de emissao: 0,5 g CO2 / (kg . km); limite 300 g CO2/kg  => arco valido se dist <= 600 km
  - m = 3 (no maximo 3 CDs instalados; cada CD comporta no maximo 1 torrefadora, ha 3 torrefadoras)
  - pen_e = 2 R$/kg (penalidade de estoque)
"""

import math
import openpyxl
import pulp

# --------- premissas globais ----------
CUSTO_KM = 1.0          # R$ por km por viagem
FATOR_EMISSAO = 0.5     # g CO2 por kg por km
PEN_ESTOQUE = 2.0       # R$ por kg estocado
M_MAX_CD = 3            # numero maximo de CDs instalados


def haversine(a, b):
    """Distancia em km entre (lat,lon) a e b."""
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dla, dlo = la2 - la1, lo2 - lo1
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def load(xlsx):
    """Carrega uma planilha de cenario para um dicionario de dados."""
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    sheets = {ws.title: list(ws.iter_rows(values_only=True)) for ws in wb.worksheets}

    params = {r[0]: r[1] for r in sheets['Parametros'][1:] if r[0] is not None}
    fornecedores = [{'cidade': r[0], 'pos': (r[1], r[2]), 'oferta': r[3]}
                    for r in sheets['Fornecedores'][1:] if r[0] is not None]
    clientes = [{'cidade': r[0], 'pos': (r[1], r[2]), 'demanda': r[3]}
                for r in sheets['Clientes'][1:] if r[0] is not None]
    candidatos = [{'cidade': r[0], 'pos': (r[1], r[2]), 'fixo': r[3]}
                  for r in sheets['Candidatos'][1:] if r[0] is not None]
    torrefadoras = [{'nome': r[0], 'cap': r[1], 'proc': r[2], 'tempo': r[3]}
                    for r in sheets['Torrefadoras'][1:] if r[0] is not None]

    return {
        'nome': xlsx,
        'cap_caminhao': params['capacidade_caminhao_kg'],
        'limite_emissao': params['limite_maximo_emissao_g_CO2_kg'],
        'fornecedores': fornecedores,
        'clientes': clientes,
        'candidatos': candidatos,
        'torrefadoras': torrefadoras,
    }


def build_and_solve(data, m_max=M_MAX_CD, pen_e=PEN_ESTOQUE,
                    fator_emissao=FATOR_EMISSAO, custo_km=CUSTO_KM,
                    limite_emissao=None, demanda_exata=True, pen_falta=None,
                    cap_caminhao=None, fixos_override=None, msg=False):
    """
    Constroi e resolve o MILP. Retorna um dicionario de solucao.

    Parametros de flexibilizacao (usados nos cenarios bonus):
      - limite_emissao: sobrepoe o limite (g CO2/kg) para aperto de emissoes
      - demanda_exata=False + pen_falta: permite demanda nao atendida com penalidade
      - cap_caminhao: sobrepoe a capacidade do caminhao
      - fixos_override: dict {cidade: custo} para alterar custos de instalacao
    """
    I = data['fornecedores']
    J = data['clientes']
    K = data['candidatos']
    T = data['torrefadoras']
    cap = cap_caminhao if cap_caminhao is not None else data['cap_caminhao']
    lim_emis = limite_emissao if limite_emissao is not None else data['limite_emissao']

    fixos = {k['cidade']: k['fixo'] for k in K}
    if fixos_override:
        fixos.update(fixos_override)

    s = {i: I[i]['oferta'] for i in range(len(I))}
    d = {j: J[j]['demanda'] for j in range(len(J))}
    f = {k: fixos[K[k]['cidade']] for k in range(len(K))}
    q = {t: T[t]['cap'] for t in range(len(T))}
    p = {t: T[t]['proc'] for t in range(len(T))}

    nI, nJ, nK, nT = len(I), len(J), len(K), len(T)
    Mbig = sum(s.values())

    # distancias e limite de emissao por arco (dist_max = lim/fator)
    dist_max = lim_emis / fator_emissao
    dik = {(i, k): haversine(I[i]['pos'], K[k]['pos']) for i in range(nI) for k in range(nK)}
    dkj = {(k, j): haversine(K[k]['pos'], J[j]['pos']) for k in range(nK) for j in range(nJ)}
    arcos_ik = [(i, k) for i in range(nI) for k in range(nK) if dik[(i, k)] <= dist_max]
    arcos_kj = [(k, j) for k in range(nK) for j in range(nJ) if dkj[(k, j)] <= dist_max]
    # CDs proibidos (custo fixo infinito) ficam fora
    cd_proibido = {k for k in range(nK) if f[k] >= 1e20}

    prob = pulp.LpProblem('cadeia_cafe', pulp.LpMinimize)

    x = {(i, k): pulp.LpVariable(f'x_{i}_{k}', lowBound=0) for (i, k) in arcos_ik}
    y = {(k, j): pulp.LpVariable(f'y_{k}_{j}', lowBound=0) for (k, j) in arcos_kj}
    z = {(k, t): pulp.LpVariable(f'z_{k}_{t}', cat='Binary') for k in range(nK) for t in range(nT)}
    w = {k: pulp.LpVariable(f'w_{k}', cat='Binary') for k in range(nK)}
    u = {(i, k, t): pulp.LpVariable(f'u_{i}_{k}_{t}', lowBound=0)
         for (i, k) in arcos_ik for t in range(nT)}
    e = {k: pulp.LpVariable(f'e_{k}', lowBound=0) for k in range(nK)}
    n_ik = {(i, k): pulp.LpVariable(f'n_{i}_{k}', lowBound=0, cat='Integer') for (i, k) in arcos_ik}
    n_kj = {(k, j): pulp.LpVariable(f'm_{k}_{j}', lowBound=0, cat='Integer') for (k, j) in arcos_kj}

    falta = None
    if not demanda_exata:
        falta = {j: pulp.LpVariable(f'falta_{j}', lowBound=0) for j in range(nJ)}

    # Funcao objetivo (1) + extensoes
    transporte = pulp.lpSum(custo_km * dik[(i, k)] * n_ik[(i, k)] for (i, k) in arcos_ik) \
        + pulp.lpSum(custo_km * dkj[(k, j)] * n_kj[(k, j)] for (k, j) in arcos_kj)
    instalacao = pulp.lpSum(f[k] * w[k] for k in range(nK) if k not in cd_proibido)
    producao = pulp.lpSum(p[t] * u[(i, k, t)] for (i, k) in arcos_ik for t in range(nT))
    estoque = pulp.lpSum(pen_e * e[k] for k in range(nK))
    obj = transporte + instalacao + producao + estoque
    if not demanda_exata:
        obj += pulp.lpSum(pen_falta * falta[j] for j in range(nJ))
    prob += obj

    # (2)/(3) oferta
    for i in range(nI):
        saida = pulp.lpSum(x[(i, k)] for k in range(nK) if (i, k) in x)
        prob += saida <= s[i]
        prob += saida == s[i]                     # escoa toda a oferta (eq. 3)

    # (4)/(5) demanda
    for j in range(nJ):
        entrada = pulp.lpSum(y[(k, j)] for k in range(nK) if (k, j) in y)
        if demanda_exata:
            prob += entrada >= d[j]
            prob += entrada <= d[j]
        else:
            prob += entrada + falta[j] == d[j]    # permite falta com penalidade
            prob += entrada <= d[j]

    # (6) conservacao de fluxo no CD
    for k in range(nK):
        entra = pulp.lpSum(x[(i, k)] for i in range(nI) if (i, k) in x)
        sai = pulp.lpSum(y[(k, j)] for j in range(nJ) if (k, j) in y)
        prob += entra == sai + e[k]

    # (7) torrefadora so em CD instalado / no maximo 1 por CD
    for k in range(nK):
        prob += pulp.lpSum(z[(k, t)] for t in range(nT)) <= w[k]
        if k in cd_proibido:
            prob += w[k] == 0

    # (8) capacidade de processamento do CD
    for k in range(nK):
        entra = pulp.lpSum(x[(i, k)] for i in range(nI) if (i, k) in x)
        prob += entra <= pulp.lpSum(q[t] * z[(k, t)] for t in range(nT))

    # (9) cada torrefadora em no maximo 1 CD
    for t in range(nT):
        prob += pulp.lpSum(z[(k, t)] for k in range(nK)) <= 1

    # (10) numero maximo de CDs
    prob += pulp.lpSum(w[k] for k in range(nK)) <= m_max

    # (11)(12)(13) coerencia processamento x torrefadora
    for (i, k) in arcos_ik:
        prob += pulp.lpSum(u[(i, k, t)] for t in range(nT)) == x[(i, k)]
        for t in range(nT):
            prob += u[(i, k, t)] <= x[(i, k)]
            prob += u[(i, k, t)] <= Mbig * z[(k, t)]

    # viagens (caminhao)
    for (i, k) in arcos_ik:
        prob += x[(i, k)] <= cap * n_ik[(i, k)]
    for (k, j) in arcos_kj:
        prob += y[(k, j)] <= cap * n_kj[(k, j)]

    solver = pulp.PULP_CBC_CMD(msg=msg)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]

    sol = {'data': data, 'status': status, 'cap': cap, 'lim_emis': lim_emis,
           'm_max': m_max, 'pen_e': pen_e}
    if status != 'Optimal':
        return sol

    val = lambda v: (v.value() or 0.0)
    sol['fo'] = pulp.value(prob.objective)
    sol['custo_transporte'] = sum(custo_km * dik[(i, k)] * val(n_ik[(i, k)]) for (i, k) in arcos_ik) \
        + sum(custo_km * dkj[(k, j)] * val(n_kj[(k, j)]) for (k, j) in arcos_kj)
    sol['custo_instalacao'] = sum(f[k] * val(w[k]) for k in range(nK) if k not in cd_proibido)
    sol['custo_producao'] = sum(p[t] * val(u[(i, k, t)]) for (i, k) in arcos_ik for t in range(nT))
    sol['custo_estoque'] = sum(pen_e * val(e[k]) for k in range(nK))
    sol['estoque_total'] = sum(val(e[k]) for k in range(nK))
    if not demanda_exata:
        sol['falta_total'] = sum(val(falta[j]) for j in range(nJ))
        sol['custo_falta'] = pen_falta * sol['falta_total']
        sol['falta_por_cliente'] = {J[j]['cidade']: val(falta[j])
                                    for j in range(nJ) if val(falta[j]) > 1e-6}

    # CDs instalados e torrefadoras
    cds = []
    for k in range(nK):
        if val(w[k]) > 0.5:
            torrs = [T[t]['nome'] for t in range(nT) if val(z[(k, t)]) > 0.5]
            recebe = sum(val(x[(i, k)]) for i in range(nI) if (i, k) in x)
            envia = sum(val(y[(k, j)]) for j in range(nJ) if (k, j) in y)
            cds.append({'cidade': K[k]['cidade'], 'torrefadoras': torrs,
                        'recebe': recebe, 'envia': envia, 'estoque': val(e[k]),
                        'fixo': f[k]})
    sol['cds'] = cds
    sol['torrefadoras_usadas'] = sorted({t for cd in cds for t in cd['torrefadoras']})

    # fluxos e viagens
    sol['fluxo_ik'] = [(I[i]['cidade'], K[k]['cidade'], val(x[(i, k)]), int(round(val(n_ik[(i, k)]))))
                       for (i, k) in arcos_ik if val(x[(i, k)]) > 1e-6]
    sol['fluxo_kj'] = [(K[k]['cidade'], J[j]['cidade'], val(y[(k, j)]), int(round(val(n_kj[(k, j)]))))
                       for (k, j) in arcos_kj if val(y[(k, j)]) > 1e-6]
    sol['viagens_total'] = sum(int(round(val(n_ik[(i, k)]))) for (i, k) in arcos_ik) \
        + sum(int(round(val(n_kj[(k, j)]))) for (k, j) in arcos_kj)
    sol['viagens_ik'] = sum(int(round(val(n_ik[(i, k)]))) for (i, k) in arcos_ik)
    sol['viagens_kj'] = sum(int(round(val(n_kj[(k, j)]))) for (k, j) in arcos_kj)

    # emissoes (g CO2 = fator * dist * fluxo)
    sol['co2_total'] = sum(fator_emissao * dik[(i, k)] * val(x[(i, k)]) for (i, k) in arcos_ik) \
        + sum(fator_emissao * dkj[(k, j)] * val(y[(k, j)]) for (k, j) in arcos_kj)
    sol['n_arcos_proibidos'] = len([1 for i in range(nI) for k in range(nK) if dik[(i, k)] > dist_max]) \
        + len([1 for k in range(nK) for j in range(nJ) if dkj[(k, j)] > dist_max])
    sol['km_total'] = sum(dik[(i, k)] * int(round(val(n_ik[(i, k)]))) for (i, k) in arcos_ik) \
        + sum(dkj[(k, j)] * int(round(val(n_kj[(k, j)]))) for (k, j) in arcos_kj)
    return sol


def plot_map(sol, png, titulo=None, destacar_falta=False):
    """Gera o mapa de rotas (lon x lat) com fornecedores, CDs, clientes e fluxos."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    data = sol['data']
    pos = {}
    for grp in ('fornecedores', 'clientes', 'candidatos'):
        for e in data[grp]:
            pos.setdefault(e['cidade'], e['pos'])

    fig, ax = plt.subplots(figsize=(7, 7))

    # arcos fornecedor -> CD
    for (a, b, fluxo, nv) in sol.get('fluxo_ik', []):
        (la, lo), (lb, lob) = pos[a], pos[b]
        ax.plot([lo, lob], [la, lb], color='#8c8c8c', lw=0.8, ls='--', zorder=1)
    # arcos CD -> cliente
    for (a, b, fluxo, nv) in sol.get('fluxo_kj', []):
        (la, lo), (lb, lob) = pos[a], pos[b]
        ax.plot([lo, lob], [la, lb], color='#1f77b4', lw=0.7, alpha=0.6, zorder=1)

    fx = [e['pos'] for e in data['fornecedores']]
    cx = [e['pos'] for e in data['clientes']]
    ax.scatter([p[1] for p in fx], [p[0] for p in fx], marker='s', s=55,
               c='#2ca02c', edgecolors='k', linewidths=0.4, label='Fornecedor', zorder=3)
    ax.scatter([p[1] for p in cx], [p[0] for p in cx], marker='o', s=28,
               c='#d62728', edgecolors='k', linewidths=0.3, label='Cliente', zorder=3)
    cds = sol.get('cds', [])
    ax.scatter([pos[cd['cidade']][1] for cd in cds], [pos[cd['cidade']][0] for cd in cds],
               marker='*', s=320, c='#ff7f0e', edgecolors='k', linewidths=0.6,
               label='CD instalado', zorder=4)
    for cd in cds:
        la, lo = pos[cd['cidade']]
        ax.annotate(cd['cidade'], (lo, la), fontsize=7, fontweight='bold',
                    xytext=(4, 4), textcoords='offset points', zorder=5)

    if destacar_falta and sol.get('falta_por_cliente'):
        for cidade in sol['falta_por_cliente']:
            la, lo = pos[cidade]
            ax.scatter([lo], [la], marker='x', s=120, c='k', linewidths=1.8, zorder=6)

    ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude')
    ax.set_title(titulo or '', fontsize=10)
    ax.legend(loc='best', fontsize=8, framealpha=0.9)
    ax.grid(True, ls=':', alpha=0.4)
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    plt.close(fig)
