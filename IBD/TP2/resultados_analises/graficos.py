import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os  # <-- ADICIONE ESTA LINHA PARA CORRIGIR O ERRO

# Configuração padrão para os gráficos
sns.set_theme(style="whitegrid", palette="viridis")
output_graficos_dir = 'graficos_analise'
if not os.path.exists(output_graficos_dir):
    os.makedirs(output_graficos_dir)

# --- Análise 1: Alunos por Campus ---
df1 = pd.read_csv('resultados_analises/1_alunos_por_campus.csv')
plt.figure(figsize=(12, 8))
sns.barplot(data=df1, x='total_alunos', y='campus')
plt.title('Distribuição de Alunos por Campus', fontsize=16)
plt.xlabel('Número Total de Alunos', fontsize=12)
plt.ylabel('Campus', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '1_alunos_por_campus.png'))
plt.show()


# --- Análise 2: Demanda por Curso (Top 15) ---
df2 = pd.read_csv('resultados_analises/2_demanda_por_curso.csv')
plt.figure(figsize=(12, 10))
sns.barplot(data=df2.head(15), x='total_alunos', y='curso')
plt.title('Top 15 Cursos com Maior Número de Alunos', fontsize=16)
plt.xlabel('Número de Alunos Matriculados', fontsize=12)
plt.ylabel('Curso', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '2_demanda_por_curso.png'))
plt.show()


# --- Análise 3: Distribuição de Gênero por Departamento ---
df3 = pd.read_csv('resultados_analises/3_genero_por_departamento.csv')
plt.figure(figsize=(12, 8))
sns.barplot(data=df3, y='departamento', x='quantidade', hue='sexo', palette={'M': '#4682B4', 'F': '#FFC0CB'})
plt.title('Distribuição de Gênero por Departamento', fontsize=16)
plt.xlabel('Quantidade de Alunos', fontsize=12)
plt.ylabel('Departamento', fontsize=12)
plt.legend(title='Sexo')
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '3_genero_por_departamento.png'))
plt.show()


# --- Análise 4: Tendência de Ingressantes ao Longo do Tempo ---
df4 = pd.read_csv('resultados_analises/4_tendencia_ingressantes_tempo.csv')
plt.figure(figsize=(15, 7))
sns.lineplot(data=df4, x='periodo_inicial', y='quantidade_ingressantes', marker='o', sort=False)
plt.title('Evolução do Número de Ingressantes por Período', fontsize=16)
plt.xlabel('Período de Ingresso', fontsize=12)
plt.ylabel('Quantidade de Novos Alunos', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '4_tendencia_ingressantes.png'))
plt.show()


# --- Análise 5: Cursos com Mais Alunos em Atraso Potencial ---
df5 = pd.read_csv('resultados_analises/5_atrasados_por_curso.csv')
plt.figure(figsize=(12, 10))
sns.barplot(data=df5, x='quantidade_alunos_atrasados', y='nome_curso')
plt.title('Top 15 Cursos com Mais Alunos Ingressantes Antes de 2020', fontsize=16)
plt.xlabel('Nº de Alunos com Possível Atraso', fontsize=12)
plt.ylabel('Curso', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '5_atrasados_por_curso.png'))
plt.show()

# --- Análise 6: Proporção de Ingressantes de 2024 por Turno ---
df6 = pd.read_csv('resultados_analises/6_ingressantes_2024_por_turno.csv')
plt.figure(figsize=(8, 8))
plt.pie(df6['total_alunos'], labels=df6['turno'], autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
plt.title('Proporção de Ingressantes em 2024 por Turno', fontsize=16)
plt.ylabel('')
plt.tight_layout()
plt.savefig(os.path.join(output_graficos_dir, '6_ingressantes_2024_por_turno.png'))
plt.show()