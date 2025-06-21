import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Dados processados da análise dos logs. Cada linha é um ponto no tempo
# com o número cumulativo de pacotes entregues por cada sistema.
csv_data = """Tempo,Pacotes_Entregues_Simples,Pacotes_Entregues_Otimizado
0,0,0
206,1,1
216,2,1
225,2,6
305,3,6
316,4,12
318,4,13
335,4,18
403,5,18
415,5,23
416,6,23
435,6,28
500,7,28
501,7,29
504,7,34
507,7,35
510,7,40
516,7,41
535,7,46
605,7,47
606,7,48
609,7,49
612,7,50
616,8,50
691,9,50
716,10,50
785,11,50
816,12,50
878,13,50
916,14,50
970,15,50
1031,15,50
1061,16,50
1116,17,50
1151,18,50
1216,19,50
1240,20,50
1316,21,50
1328,22,50
1415,23,50
1501,24,50
1516,25,50
1586,26,50
1616,27,50
1670,28,50
1716,29,50
1753,30,50
1816,31,50
1835,32,50
1916,33,50
1942,34,50
2016,35,50
2075,36,50
2116,37,50
2153,38,50
2230,39,50
2306,40,50
2316,41,50
2381,42,50
2416,43,50
2455,44,50
2516,45,50
2528,46,50
2600,47,50
2671,48,50
2716,49,50
2741,49,50
2800,49,50
2810,49,50
2816,49,50
2868,49,50
2878,49,50
2916,49,50
2935,49,50
2945,49,50
3001,49,50
3011,49,50
3066,49,50
3076,49,50
3130,49,50
3140,49,50
3193,49,50
3203,49,50
3255,49,50
3265,49,50
3316,49,50
3326,49,50
3376,49,50
3386,49,50
3435,49,50
3445,49,50
3493,49,50
3503,49,50
3550,49,50
3560,49,50
3606,49,50
3616,49,50
3661,49,50
3671,49,50
3715,49,50
3725,49,50
3768,49,50
3778,49,50
3820,49,50
3830,49,50
3871,49,50
3881,50,50
"""

# Lê os dados em um DataFrame do pandas
data = pd.read_csv(StringIO(csv_data))

# --- Gera o Gráfico ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))

# Plota as duas linhas usando um gráfico de degraus (steps), que é mais preciso para eventos discretos
ax.step(data['Tempo'], data['Pacotes_Entregues_Otimizado'], where='post', 
        color='forestgreen', linewidth=2.5, label='Sistema Otimizado')

ax.step(data['Tempo'], data['Pacotes_Entregues_Simples'], where='post', 
        color='orangered', linewidth=2.5, linestyle='--', label='Sistema Base (Não Otimizado)')

# Configura títulos, legendas e eixos
ax.set_title('Prova de Valor: Comparativo de Eficiência Logística', fontsize=18, pad=20)
ax.set_xlabel('Tempo de Simulação', fontsize=14)
ax.set_ylabel('Total de Pacotes Entregues', fontsize=14)
ax.legend(fontsize=12, loc='best')
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid(True, which='both', linestyle=':', linewidth=0.7)

# Define limites para melhor visualização
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

# Salva a imagem final
plt.tight_layout()
plt.savefig("comparativo_sistemas.png", dpi=300)

print("Gráfico 'comparativo_sistemas.png' foi gerado com sucesso!")