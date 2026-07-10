# -*- coding: utf-8 -*-
"""
Cenarios bonus (analises adicionais para insights):
  B1 - Cenario 3 relaxado: permite demanda nao atendida com penalidade -> quantifica colapso.
  B2 - Aperto do limite de emissao: trade-off custo x CO2 (fronteira).
  B3 - Varredura da capacidade do caminhao: custo de transporte x numero de viagens.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from solver import load, build_and_solve, plot_map


def b1_demanda_relaxada():
    print('=' * 70)
    print('B1 - Cenario 3 relaxado (demanda > oferta): variavel de falta')
    data = load('cenario_3_aumento_demanda.xlsx')
    oferta = sum(i['oferta'] for i in data['fornecedores'])
    demanda = sum(j['demanda'] for j in data['clientes'])
    print(f'  oferta {oferta:.0f} | demanda {demanda:.0f} | deficit estrutural {demanda-oferta:.0f} kg')
    # penalidade de falta alta (R$/kg) para priorizar atendimento maximo
    sol = build_and_solve(data, demanda_exata=False, pen_falta=50.0)
    print(f"  status: {sol['status']}  FO R$ {sol['fo']:,.2f}")
    print(f"  falta total: {sol['falta_total']:.0f} kg  (custo de falta R$ {sol['custo_falta']:,.0f})")
    print(f"  transporte R$ {sol['custo_transporte']:,.0f} | instalacao R$ {sol['custo_instalacao']:,.0f} | producao R$ {sol['custo_producao']:,.0f}")
    print('  Clientes com demanda nao atendida:')
    for cidade, q in sorted(sol['falta_por_cliente'].items(), key=lambda kv: -kv[1]):
        print(f'    - {cidade:<24} {q:.0f} kg')
    print(f"  CDs instalados: {[cd['cidade'] for cd in sol['cds']]}")
    plot_map(sol, 'bonus_falta_mapa.png',
             titulo=f"B1 - Demanda relaxada (falta total {sol['falta_total']:.0f} kg)\n"
                    f"x = cliente com demanda nao atendida", destacar_falta=True)
    print('  -> mapa salvo: bonus_falta_mapa.png')
    return sol


def b2_emissoes():
    print('=' * 70)
    print('B2 - Aperto do limite de emissao (trade-off custo x CO2)')
    data = load('cenario_1_base.xlsx')
    limites = [300, 250, 200, 150, 120, 100, 80]
    xs, custos, co2s = [], [], []
    for lim in limites:
        sol = build_and_solve(data, limite_emissao=lim)
        if sol['status'] != 'Optimal':
            print(f'  limite {lim} g/kg -> {sol["status"]}')
            xs.append(lim); custos.append(None); co2s.append(None)
            continue
        dmax = lim / 0.5
        print(f"  limite {lim:>3} g/kg (dist_max {dmax:.0f} km) -> custo R$ {sol['fo']:,.0f} | CO2 {sol['co2_total']/1000:.1f} kg | CDs {[c['cidade'] for c in sol['cds']]}")
        xs.append(lim); custos.append(sol['fo']); co2s.append(sol['co2_total'] / 1000)

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    xv = [x for x, c in zip(xs, custos) if c is not None]
    cv = [c for c in custos if c is not None]
    ev = [c for c in co2s if c is not None]
    ax1.plot(xv, cv, 'o-', color='#d62728', label='Custo total')
    ax1.set_xlabel('Limite de emissao (g CO2/kg)')
    ax1.set_ylabel('Custo total (R$)', color='#d62728')
    ax1.tick_params(axis='y', labelcolor='#d62728')
    ax1.invert_xaxis()
    ax2 = ax1.twinx()
    ax2.plot(xv, ev, 's--', color='#2ca02c', label='CO2 emitido')
    ax2.set_ylabel('CO2 emitido (kg)', color='#2ca02c')
    ax2.tick_params(axis='y', labelcolor='#2ca02c')
    ax1.set_title('B2 - Trade-off: aperto do limite de emissao')
    ax1.grid(True, ls=':', alpha=0.5)
    fig.tight_layout()
    fig.savefig('bonus_emissao.png', dpi=130)
    plt.close(fig)
    print('  -> figura salva: bonus_emissao.png')


def b3_capacidade():
    print('=' * 70)
    print('B3 - Varredura da capacidade do caminhao (viagens x custo)')
    data = load('cenario_1_base.xlsx')
    caps = [200, 250, 300, 400, 500, 700, 1000]
    xs, transp, viag, fo = [], [], [], []
    for c in caps:
        sol = build_and_solve(data, cap_caminhao=c)
        if sol['status'] != 'Optimal':
            print(f'  cap {c} -> {sol["status"]}'); continue
        print(f"  cap {c:>4} kg -> viagens {sol['viagens_total']:>3} | transporte R$ {sol['custo_transporte']:,.0f} | custo total R$ {sol['fo']:,.0f}")
        xs.append(c); transp.append(sol['custo_transporte']); viag.append(sol['viagens_total']); fo.append(sol['fo'])

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.plot(xs, viag, 'o-', color='#1f77b4', label='Numero de viagens')
    ax1.set_xlabel('Capacidade do caminhao (kg)')
    ax1.set_ylabel('Numero de viagens', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax2 = ax1.twinx()
    ax2.plot(xs, transp, 's--', color='#ff7f0e', label='Custo de transporte')
    ax2.set_ylabel('Custo de transporte (R$)', color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    ax1.axvline(300, color='gray', ls=':', alpha=0.7)
    ax1.set_title('B3 - Impacto da capacidade do caminhao')
    ax1.grid(True, ls=':', alpha=0.5)
    fig.tight_layout()
    fig.savefig('bonus_capacidade.png', dpi=130)
    plt.close(fig)
    print('  -> figura salva: bonus_capacidade.png')


if __name__ == '__main__':
    b1_demanda_relaxada()
    b2_emissoes()
    b3_capacidade()
    print('\nBonus concluido.')
