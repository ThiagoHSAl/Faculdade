#ifndef ORDENADORUNIVERSAL_HPP
#define ORDENADORUNIVERSAL_HPP


typedef struct estatisticas{
  int cmp;
  int move;
  int calls;
} estatisticas;

class OrdenadorUniversal {
private:
    int* vetorOriginal;
    int tamanho;
    int limiarCusto;
    double a, b, c;

    // Atributos para calibragem de partição
    estatisticas s;
    int tamanhosTestados[10];
    double custosQS[10];
    double custosIS[10];
    int numeroQuebras;

public:
    OrdenadorUniversal(int* v, int t, int custo, double a_, double b_, double c_);
    int determinaLimiarParticao();
    int determinaLimiarQuebra(int menorTamanhoParticao);
    void calculaNovaFaixa(int indexadorTeste, int melhorIndice, int* menorTamanhoParticao, int* maiorTamanhoParticao, int* passoTestes, double* diferencaCusto, char identificador);
    void escolheAlgoritmo(int menorTamanhoParticao, int limiarQuebras);
    void registraEstatisticas(char identificador, int indexador);
    void imprimeEstatisticas(char identificador, int indexador);
    int getTamanho(int indexador);
    int menorCusto();
    int menorDiferenca();
    void resetCustos();
    int* copiaVetor(int tamanho);
    int* vetorComQuebra(int* vetor, int quebras);
    void print(int* vetor);
    // ...
};

int contaQuebras(int* vetor, int inicio, int final);
#endif