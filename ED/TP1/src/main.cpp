#include <iostream>
#include <random>
#include "OrdenadorUniversal.hpp"
#include "AlgoritmosOrdenacao.hpp"
#include <fstream>

int main(int argc, char* argv[]){
    int tamanho, particao, seed, elemento, quebras;
    double  limiarCusto, a, b, c;
    int* vetor;
    estatisticas s;

    if (argc != 2) {
        std::cerr << "Erro: É necessário fornecer o nome do arquivo como argumento." << std::endl;
        return 1;
    }

    std::string nome_arquivo = argv[1];
    std::ifstream arquivo(nome_arquivo);

    if (!arquivo) {
        std::cerr << "Erro: Não foi possível abrir o arquivo " << nome_arquivo << std::endl;
        return 1;
    }

    arquivo >> seed;
    arquivo >> limiarCusto;
    arquivo >> a;
    arquivo >> b;
    arquivo >> c;
    arquivo >> tamanho;

    vetor = new int[tamanho];

    for(int i = 0; i < tamanho; i++){
        arquivo >> elemento;
        vetor[i] = elemento;
    }

    OrdenadorUniversal teste(vetor, tamanho, limiarCusto, a, b, c, seed);
    quebras = contaQuebras(vetor, 0, tamanho);
    std::cout << "size " << tamanho << " seed " << seed << " breaks " << quebras << std::endl;
    particao = teste.determinaLimiarParticao();
    particao = teste.determinaLimiarQuebra(particao);
}