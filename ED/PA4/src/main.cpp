#include <iostream>    
#include <algorithm> 

#include "Aresta.hpp" 
#include "DSU.hpp"   
#include "Heap.hpp"   

int main() {
    int n, m; 

    std::cin >> n >> m;

    DSU dsu(n);

    for (int i = 0; i < n; ++i) {
        dsu.Make(i);
    }

    Heap heap(m);

    for (int i = 0; i < m; ++i) {
        int u, v, custo;
        std::cin >> u >> v >> custo; 
        Aresta aresta = {u, v, custo}; 
        heap.Inserir(aresta);         
    }

    long long custo_total_mst = 0; 
    int arestas_adicionadas = 0;   

    while (!heap.Vazio() && arestas_adicionadas < n - 1) {
        Aresta e = heap.Remover(); 

        if (dsu.Find(e.u) != dsu.Find(e.v)) {
            dsu.Union(e.u, e.v);         
            custo_total_mst += e.custo;  
            arestas_adicionadas++;     
        }
    }

    std::cout << custo_total_mst << std::endl;

    return 0;
}

