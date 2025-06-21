import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

# Dados fornecidos por você
csv_data = """Capacidade,TempoUser
1,0m40.310s
2,0m22.333s
3,0m15.502s
4,0m10.894s
5,0m10.202s
6,0m9.264s
7,0m9.010s
8,0m8.305s
9,0m8.457s
10,0m9.409s
11,0m9.277s
12,0m8.731s
13,0m8.507s
14,0m9.016s
15,0m8.706s
16,0m8.914s
17,0m10.196s
18,0m9.592s
19,0m9.771s
20,0m9.180s
21,0m8.500s
22,0m8.637s
23,0m9.220s
24,0m8.529s
25,0m8.317s
26,0m9.002s
27,0m8.188s
28,0m8.440s
29,0m8.226s
30,0m8.784s"""

# Lê os dados
data = pd.read_csv(StringIO(csv_data))

# Converte o tempo para segundos
def convert_time_to_seconds(time_str):
    time_str = time_str.replace('m', ' ').replace('s', '')
    minutes, seconds = map(float, time_str.split())
    return minutes * 60 + seconds

data['TempoSegundos'] = data['TempoUser'].apply(convert_time_to_seconds)

# --- Gera o Gráfico ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))

# Plota os dados com pontos e linhas para melhor visualização da tendência
ax.plot(data['Capacidade'], data['TempoSegundos'], marker='o', linestyle='-', color='darkcyan', label='Tempo de Execução Real')

# Configura títulos e legendas, incluindo os parâmetros fixos no título
ax.set_title('Análise de Desempenho: Tempo de Execução vs. Capacidade de Transporte\n(Fixo: 500 Armazéns, 5000 Pacotes)', fontsize=18, pad=20)
ax.set_xlabel('Capacidade de Transporte (pacotes por viagem)', fontsize=14)
ax.set_ylabel('Tempo de Execução "User" (Segundos)', fontsize=14)
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Salva a imagem
plt.tight_layout()
plt.savefig("analise_desempenho_capacidade.png", dpi=300)
plt.close()