import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# 1. Criar o grafo
G = nx.Graph()

# Adicionar nós (0=Origem, 3=Destino, 1=Rota Rápida, 2=Rota Lenta)
G.add_nodes_from([0, 1, 2, 3])

# Adicionar arestas com atributos de latência e capacidade
# Rota A: 0 -> 1 -> 3 (Rápida, Baixa Capacidade)
G.add_edge(0, 1, latency=5, capacity=1)
G.add_edge(1, 3, latency=5, capacity=1)

# Rota B: 0 -> 2 -> 3 (Lenta, Alta Capacidade)
G.add_edge(0, 2, latency=20, capacity=10)
G.add_edge(2, 3, latency=20, capacity=10)

# 2. Definir o layout (posição dos nós) para a forma de diamante
pos = {0: [-1, 0], 1: [0, 0.7], 2: [0, -0.7], 3: [1, 0]}

# 3. Definir atributos visuais para clareza
# Cor dos nós: destaca origem e destino
node_colors = ['#ff6b6b' if n in [0, 3] else '#4ecdc4' for n in G.nodes()]
node_sizes = [1500 if n in [0, 3] else 1000 for n in G.nodes()]

# Espessura das arestas representa a capacidade
edge_widths = [d['capacity'] / 2 for u, v, d in G.edges(data=True)]
# Cor das arestas representa a rota
edge_colors = ['#ff6b6b' if d['capacity'] == 1 else '#4ecdc4' for u, v, d in G.edges(data=True)]

# Rótulos das arestas mostram a latência
edge_labels = nx.get_edge_attributes(G, 'latency')

# 4. Desenhar o grafo
fig, ax = plt.subplots(figsize=(12, 8))

# Desenha os nós
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, ax=ax)

# Desenha as arestas com espessura e cor variáveis
nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.8, ax=ax)

# Desenha os rótulos dos nós
nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold', font_color='white', ax=ax)

# Desenha os rótulos das arestas (latência)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, font_color='black',
                             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

# 5. Criar uma legenda customizada para explicar a visualização
legend_elements = [
    mlines.Line2D([0], [0], color='#ff6b6b', lw=1, label='Rota Rápida (Latência 5, Capacidade 1)'),
    mlines.Line2D([0], [0], color='#4ecdc4', lw=5, label='Rota Lenta (Latência 20, Capacidade 10)'),
    mlines.Line2D([0], [0], marker='o', color='w', label='Armazém de Origem/Destino',
                   markerfacecolor='#ff6b6b', markersize=15),
    mlines.Line2D([0], [0], marker='o', color='w', label='Armazém Intermediário',
                   markerfacecolor='#4ecdc4', markersize=15)
]

# --- CORREÇÃO APLICADA AQUI ---
# A posição vertical da legenda (bbox_to_anchor) foi aumentada de 1.1 para 1.2
ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, fontsize=12)

# 6. Finalizar e salvar o arquivo
ax.set_title("Grafo do Experimento de Prova de Valor", fontsize=20, pad=20)
plt.axis('off')
plt.tight_layout()
plt.savefig("grafo_experimento.png", dpi=300, bbox_inches='tight')

print("Arquivo 'grafo_experimento.png' salvo com sucesso!")