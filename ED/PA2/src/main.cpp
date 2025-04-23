#include "graph.hpp"
#include "ListaAdjacencia.hpp"
#include "TipoCelula.hpp"
#include <iostream>

int main(int argc, char* argv[]){
    Grafo grafo;
    int vertices;
    int vizinho;
    int contador_vizinhos;

    std::cin >> vertices;

    for(int i = 0; i < vertices; i++){
        std::cin >> contador_vizinhos;
        grafo.InsereVertice();
        for(int j = 0; j < contador_vizinhos; j++){
            std::cin >> vizinho;
            grafo.InsereAresta(i,vizinho);
        }
    }

    char opcao;
    opcao = argv[1][1];

    switch (opcao){
        case 'd':{
            std::cout << grafo.QuantidadeVertices() << std::endl << grafo.QuantidadeArestas();
            std::cout << std::endl << grafo.GrauMinimo() << std::endl << grafo.GrauMaximo() << std::endl;
        }

        case 'n':{
            for(int i = 0; i < vertices; i++){
                grafo.ImprimeVizinhos(i);
            }
        }

        case 'k':{
            if(grafo.QuantidadeArestas() == (vertices * (vertices - 1) / 2)){
                std::cout << 1 << std::endl;
            }
            else{
                std::cout << 0 << std::endl;
            }
        }
    }
    
    return 0;
}