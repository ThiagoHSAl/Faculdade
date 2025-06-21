import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

# Dados que você forneceu
csv_data = """Armazens,TempoUser
10,0m0.005s
20,0m0.012s
30,0m0.028s
40,0m0.066s
50,0m0.069s
60,0m0.126s
70,0m0.190s
80,0m0.283s
90,0m0.224s
100,0m0.329s
110,0m0.495s
120,0m0.620s
130,0m0.714s
140,0m0.686s
150,0m0.714s
160,0m0.987s
170,0m1.085s
180,0m1.190s
190,0m1.358s
200,0m2.111s
210,0m2.568s
220,0m2.481s
230,0m3.553s
240,0m2.731s
250,0m4.056s
260,0m3.745s
270,0m4.043s
280,0m3.792s
290,0m4.899s
300,0m5.183s
310,0m5.784s
320,0m5.607s
330,0m6.255s
340,0m8.210s
350,0m8.341s
360,0m7.388s
370,0m9.264s
380,0m10.107s
390,0m10.008s
400,0m11.001s
410,0m10.802s
420,0m15.983s
430,0m16.762s
440,0m15.542s
450,0m16.605s
460,0m20.527s
470,0m16.243s
480,0m17.329s
490,0m19.614s
500,0m22.746s"""

# Lê os dados
data = pd.read_csv(StringIO(csv_data))

# Converte o tempo para segundos
def convert_time_to_seconds(time_str):
    time_str = time_str.replace('m', ' ').replace('s', '')
    minutes, seconds = map(float, time_str.split())
    return minutes * 60 + seconds

data['TempoSegundos'] = data['TempoUser'].apply(convert_time_to_seconds)

# --- Cria o Gráfico ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))
ax.scatter(data['Armazens'], data['TempoSegundos'], label='Tempo de Execução Real', color='royalblue', zorder=5)

# Adiciona a curva de tendência
degree = 3
coeffs = np.polyfit(data['Armazens'], data['TempoSegundos'], degree)
poly = np.poly1d(coeffs)
x_curve = np.linspace(data['Armazens'].min(), data['Armazens'].max(), 500)
y_curve = poly(x_curve)
ax.plot(x_curve, y_curve, color='crimson', linestyle='--', linewidth=2, label=f'Curva de Tendência (Polinomial Grau {degree})')

# Títulos e legendas
ax.set_title('Análise de Desempenho: Tempo de Execução vs. Número de Armazéns', fontsize=18, pad=20)
ax.set_xlabel('Número de Armazéns', fontsize=14)
ax.set_ylabel('Tempo de Execução "User" (Segundos)', fontsize=14)
ax.legend(fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Salva o gráfico como um arquivo de imagem
plt.tight_layout()
plt.savefig("analise_desempenho_armazens.png", dpi=300)

print("Gráfico 'analise_desempenho_armazens.png' foi gerado com sucesso no mesmo diretório.")