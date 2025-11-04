import pandas as pd
import matplotlib.pyplot as plt
import os

def plotar_relatorio(filename, title, xlabel, ylabel):
    """
    Função para ler um arquivo de relatório, limpar os dados
    e gerar um gráfico de desempenho.
    """
    # Verifica se o arquivo existe
    if not os.path.exists(filename):
        print(f"Aviso: O arquivo '{filename}' não foi encontrado. Pulando este gráfico.")
        return

    print(f"Processando e gerando gráfico para {filename}...")

    # Lê os dados usando pandas, ignorando linhas de comentário
    try:
        df = pd.read_csv(
            filename,
            comment='#',
            # --- CORREÇÃO AQUI ---
            # O separador agora é um ou mais espaços ('\s+'), que corresponde ao formato dos seus dados.
            sep=r'\s+',
            header=None,
            names=['Valor', 'Tempo_Medio_ms']
        )
    except Exception as e:
        print(f"Erro ao ler o arquivo {filename}: {e}")
        return
    
    # --- Geração do Gráfico ---
    plt.figure(figsize=(10, 6))
    plt.plot(df['Valor'], df['Tempo_Medio_ms'], marker='o', linestyle='-', color='b')
    
    # Adiciona títulos e rótulos
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Adiciona uma linha no eixo y=0 para referência
    plt.axhline(0, color='red', linestyle='--', linewidth=0.8)
    
    # Adiciona um grid para melhor visualização
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Ajusta as margens e salva o gráfico em um arquivo PNG
    plt.tight_layout()
    output_filename = filename.replace('.txt', '.png')
    plt.savefig(output_filename)
    print(f"Gráfico salvo como: {output_filename}")
    
    # Mostra o gráfico na tela
    plt.show()


# --- Chamadas da Função para cada Relatório ---
if __name__ == "__main__":
    plotar_relatorio(
        'relatorio_nodes.txt',
        'Desempenho vs. Número de Nós',
        'Número de Nós (nodes)',
        'Tempo Médio (ms)'
    )
    
    plotar_relatorio(
        'relatorio_numpackets.txt',
        'Desempenho vs. Número de Pacotes',
        'Número de Pacotes (numpackets)',
        'Tempo Médio (ms)'
    )

    plotar_relatorio(
        'relatorio_numclients.txt',
        'Desempenho vs. Número de Clientes',
        'Número de Clientes (numclients)',
        'Tempo Médio (ms)'
    )