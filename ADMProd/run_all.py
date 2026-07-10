# -*- coding: utf-8 -*-
"""Resolve os 5 cenarios, gera mapas e imprime os dados pedidos."""

from solver import load, build_and_solve, plot_map

CENARIOS = [
    ('Cenario 1 - Base', 'cenario_1_base.xlsx', 'mapa_cenario1.png'),
    ('Cenario 2 - Aumento da Oferta', 'cenario_2_aumento_oferta.xlsx', 'mapa_cenario2.png'),
    ('Cenario 3 - Aumento da Demanda', 'cenario_3_aumento_demanda.xlsx', 'mapa_cenario3.png'),
    ('Cenario 4 - Custo Fixo Diferenciado', 'cenario_4_custo_fixo.xlsx', 'mapa_cenario4.png'),
    ('Cenario 5 - Capacidade Reduzida do Caminhao', 'cenario_5_capacidade_caminhao.xlsx', 'mapa_cenario5.png'),
]


def resumo(sol):
    print(f"  status: {sol['status']}")
    if sol['status'] != 'Optimal':
        return
    print(f"  FO (custo total): R$ {sol['fo']:,.2f}")
    print(f"    transporte : R$ {sol['custo_transporte']:,.2f}")
    print(f"    instalacao : R$ {sol['custo_instalacao']:,.2f}")
    print(f"    producao   : R$ {sol['custo_producao']:,.2f}")
    print(f"    estoque    : R$ {sol['custo_estoque']:,.2f}  (qtd estocada {sol['estoque_total']:.1f} kg)")
    print(f"  viagens: {sol['viagens_total']} (forn->CD {sol['viagens_ik']}, CD->cli {sol['viagens_kj']}); km {sol['km_total']:,.0f}")
    print(f"  CO2 total: {sol['co2_total']/1000:,.1f} kg CO2  | arcos proibidos por emissao: {sol['n_arcos_proibidos']}")
    print(f"  CDs instalados: ")
    for cd in sol['cds']:
        print(f"    - {cd['cidade']:<22} torref {cd['torrefadoras']}  recebe {cd['recebe']:.0f}  envia {cd['envia']:.0f}  estoque {cd['estoque']:.0f}  (fixo R$ {cd['fixo']:,.0f})")
    print(f"  Torrefadoras usadas: {sol['torrefadoras_usadas']}")


def main():
    resultados = {}
    for titulo, arq, png in CENARIOS:
        print('=' * 78)
        print(titulo, f'({arq})')
        data = load(arq)
        oferta = sum(i['oferta'] for i in data['fornecedores'])
        demanda = sum(j['demanda'] for j in data['clientes'])
        print(f"  oferta total {oferta:.0f} | demanda total {demanda:.0f} | cap caminhao {data['cap_caminhao']} kg | lim emissao {data['limite_emissao']} g/kg")
        sol = build_and_solve(data)
        resumo(sol)
        if sol['status'] == 'Optimal':
            plot_map(sol, png, titulo=f"{titulo}\nCusto total: R$ {sol['fo']:,.0f}")
            print(f"  -> mapa salvo: {png}")
        else:
            print("  >>> INFACTIVEL: ver analise no relatorio / cenario bonus B1")
        resultados[titulo] = sol

    # tabela-resumo
    print('\n' + '#' * 78)
    print('TABELA RESUMO')
    print(f"{'Cenario':<42}{'FO':>12}{'Transp':>10}{'Inst':>9}{'Prod':>10}{'Estoq':>9}{'Viag':>7}{'CO2(t)':>9}")
    for titulo, _, _ in CENARIOS:
        s = resultados[titulo]
        if s['status'] == 'Optimal':
            print(f"{titulo[:40]:<42}{s['fo']:>12,.0f}{s['custo_transporte']:>10,.0f}{s['custo_instalacao']:>9,.0f}{s['custo_producao']:>10,.0f}{s['custo_estoque']:>9,.0f}{s['viagens_total']:>7}{s['co2_total']/1e6:>9.2f}")
        else:
            print(f"{titulo[:40]:<42}{'INFACTIVEL':>12}")
    return resultados


if __name__ == '__main__':
    main()
