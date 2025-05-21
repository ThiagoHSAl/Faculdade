#ifndef ORDENADORUNIVERSAL_HPP
#define ORDENADORUNIVERSAL_HPP
#include "itemT.hpp"
#include "estatisticas.hpp"

enum Algoritmo { QUICKSORT, INSERCAO };

class OrdenadorUniversal {
private:
    item_t* vetorOriginal;
    int tamanho;
    int limiarCusto;
    double a, b, c;

    // Atributos para calibragem de partição
    estatisticas Estatisticas;
    int tamanhosTestados[10];
    double custosQS[10];
    double custosIS[10];
    int numeroQuebras;
    int seed;

public:
    OrdenadorUniversal(item_t* v, int t, int custo, double a_, double b_, double c_, int seed);
    int determinaLimiarParticao();
    int determinaLimiarQuebra(int menorTamanhoParticao);
    void calculaNovaFaixa(int indexadorTeste, int melhorIndice, int* menorTamanhoParticao, int* maiorTamanhoParticao, int* passoTestes);
    void escolheAlgoritmo(int menorTamanhoParticao, int limiarQuebras);
    void registraEstatisticas(Algoritmo tipo, int indexador);
    void imprimeEstatisticas(Algoritmo tipo, int indexador);
    void imprimeAnalise(); //utilizado na analise experimental
    int getTamanho(int indexador);
    int getIndexadorTamanho(int tamanhoParticao);
    float calculaDiferenca(Algoritmo tipo, int atributoMin, int atributoMax);
    int menorCusto();
    int menorDiferenca();
    void resetCustos();
    void resetTamanhosTestados();
    item_t* copiaVetor(int tamanho);
    item_t* adicionaQuebras(item_t* vetor, int quebras);
    // ...
};


#endif