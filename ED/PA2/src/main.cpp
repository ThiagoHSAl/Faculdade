#include "graph.hpp" 
#include <iostream>
#include <string> 

int main(int argc, char* argv[]){
    if (argc < 2) {
        std::cerr << "Uso: " << argv[0] << " <operacao>" << std::endl;
        std::cerr << "Operacoes disponiveis:" << std::endl;
        std::cerr << "  -d : Dados basicos do grafo (vertices, arestas, grau min/max)" << std::endl;
        std::cerr << "  -n : Vizinhancas de cada vertice" << std::endl;
        std::cerr << "  -k : Verifica se o grafo eh completo" << std::endl;
        return 1; 
    }

    Grafo grafo;
    int vertices;
    int contador_vizinhos;
    int vizinho_vertice; 

    std::cin >> vertices;

    for(int i = 0; i < vertices; i++){
        std::cin >> contador_vizinhos;
        grafo.InsereVertice(); 
        for(int j = 0; j < contador_vizinhos; j++){
            std::cin >> vizinho_vertice;
            grafo.InsereAresta(i, vizinho_vertice);
        }
    }

    char opcao_char = ' ';
    std::string arg = argv[1]; 

    if (arg.length() == 2 && arg[0] == '-') {
        opcao_char = arg[1];
    } else {
        std::cerr << "Erro: Formato de operacao invalido. Use -d, -n ou -k." << std::endl;
        return 1;
    }

    switch (opcao_char){
        case 'd':{
            std::cout << grafo.QuantidadeVertices() << std::endl;
            std::cout << grafo.QuantidadeArestas() << std::endl; 
            std::cout << grafo.GrauMinimo() << std::endl;
            std::cout << grafo.GrauMaximo() << std::endl;
            break; 
        }

        case 'n':{
            for(int i = 0; i < vertices; i++){
                grafo.ImprimeVizinhos(i); 
            }
            break; 
        }

        case 'k':{
            if(grafo.QuantidadeArestas() == (static_cast<long long>(vertices) * (vertices - 1) / 2)){ // Use long long para evitar overflow
                std::cout << 1 << std::endl;
            }
            else{
                std::cout << 0 << std::endl;
            }
            break; 
        }

        default:{ 
            std::cerr << "Erro: Operacao '" << opcao_char << "' nao reconhecida. Use -d, -n ou -k." << std::endl;
            return 1;
        }
    }
    
    return 0;
}