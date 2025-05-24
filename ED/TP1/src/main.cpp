#include <iostream>
#include <random>
#include "OrdenadorUniversal.hpp"
#include "AlgoritmosOrdenacao.hpp"
#include <fstream>
#include <sstream>
#include "ValidacaoArquivo.hpp"
#include "AnaliseExperimental.hpp"

int main(int argc, char* argv[]){
    int tamanho, particao, seed, quebras, elemento;
    double  limiarCusto, a, b, c;
    item_t* vetor;
    estatisticas s;

    if (argc != 2) {
        std::cerr << "Erro: É necessário fornecer o nome do arquivo como argumento." << std::endl;
        return 1;
    }

    std::string nomeArquivo = argv[1];
    
    if(!verificarFormato(nomeArquivo)){
        return 0;
    }

    std::ifstream arquivo(nomeArquivo);

    arquivo >> seed;
    arquivo >> limiarCusto;
    arquivo >> a;
    arquivo >> b;
    arquivo >> c;
    arquivo >> tamanho;

    vetor = new item_t[tamanho];

    for(int i = 0; i < tamanho; i++){
        arquivo >> elemento;
        vetor[i].key = elemento;
    }

    OrdenadorUniversal teste(vetor, tamanho, limiarCusto, a, b, c, seed);
    quebras = contaQuebras(vetor, 0, tamanho);
    std::cout << "size " << tamanho << " seed " << seed << " breaks " << quebras << std::endl;
    particao = teste.determinaLimiarParticao();
    particao = teste.determinaLimiarQuebra(particao);

    //AnaliseExperimental();
}