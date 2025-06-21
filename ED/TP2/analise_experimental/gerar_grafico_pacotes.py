import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

# Dados que você forneceu
csv_data = """Pacotes,TempoUser
100,0m0.011s
200,0m0.069s
300,0m0.043s
400,0m0.092s
500,0m0.089s
600,0m0.104s
700,0m0.135s
800,0m0.205s
900,0m0.212s
1000,0m0.235s
1100,0m0.274s
1200,0m0.341s
1300,0m0.372s
1400,0m0.481s
1500,0m0.504s
1600,0m0.612s
1700,0m0.765s
1800,0m0.687s
1900,0m0.699s
2000,0m0.814s
2100,0m0.961s
2200,0m1.064s
2300,0m1.148s
2400,0m1.189s
2500,0m1.279s
2600,0m1.389s
2700,0m1.490s
2800,0m1.524s
2900,0m1.826s
3000,0m1.917s
3100,0m2.048s
3200,0m2.433s
3300,0m2.249s
3400,0m2.175s
3500,0m2.586s
3600,0m2.446s
3700,0m2.547s
3800,0m3.004s
3900,0m3.036s
4000,0m3.039s
4100,0m3.169s
4200,0m4.030s
4300,0m4.259s
4400,0m4.118s
4500,0m4.213s
4600,0m3.882s
4700,0m3.894s
4800,0m4.100s
4900,0m4.240s
5000,0m4.615s"""

# Lê os dados em um DataFrame
data = pd.read_csv(StringIO(csv_data))

# Converte o formato de tempo para segundos
def convert_time_to_seconds(time_str):
    time_str = time_str.replace('m', ' ').replace('s', '')
    minutes, seconds = map(float, time_str.split())
    return minutes * 60 + seconds

data['TempoSegundos'] = data['TempoUser'].apply(convert_time_to_seconds)

# --- Gera o Gráfico ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))

# Plota os pontos de dados reais
ax.scatter(data['Pacotes'], data['TempoSegundos'], label='Tempo de Execução Real', color='forestgreen', alpha=0.7, zorder=5)

# Adiciona uma linha de tendência linear
degree = 1
coeffs = np.polyfit(data['Pacotes'], data['TempoSegundos'], degree)
poly = np.poly1d(coeffs)
x_curve = np.linspace(data['Pacotes'].min(), data['Pacotes'].max(), 100)
y_curve = poly(x_curve)
ax.plot(x_curve, y_curve, color='orangered', linestyle='--', linewidth=2, label='Linha de Tendência (Linear)')

# Configura títulos e legendas
ax.set_title('Análise de Desempenho: Tempo de Execução vs. Número de Pacotes', fontsize=18, pad=20)
ax.set_xlabel('Número de Pacotes', fontsize=14)
ax.set_ylabel('Tempo de Execução "User" (Segundos)', fontsize=14)
ax.legend(fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Salva a imagem
plt.tight_layout()
plt.savefig("analise_desempenho_pacotes.png", dpi=300)
plt.close()