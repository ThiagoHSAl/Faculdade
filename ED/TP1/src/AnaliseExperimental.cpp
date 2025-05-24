#include <iostream>
#include <cstdlib>
#include <cmath>
#include "AnaliseExperimental.hpp"
#include "itemT.hpp"
#include "OrdenadorUniversal.hpp"
#include "AlgoritmosOrdenacao.hpp"
#include "estatisticas.hpp"
#include <chrono>
#include <iomanip>


item_t vet[VETSZ];

//ordena vet e imprime as estatísticas da ordenação
void dadosParaRegressao(){
    estatisticas s;
    resetcounter(&s);
    auto inicio = std::chrono::high_resolution_clock::now();
    quickSort(vet, 0, VETSZ-1, -1, &s);
    auto fim = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duracao = fim - inicio;
    std::cout <<"calls = " << s.calls << std::endl << "compares = " << s.cmp << std::endl << "moves = " <<s.move;
    std::cout << std::endl << "Tempo de execução: " << duracao.count() << "segundos\n";
}


void inverterVetor(item_t* vetor, int tamanho) {
    for (int i = 0; i < tamanho / 2; i++) {
        item_t temp = vetor[i];
        vetor[i] = vetor[tamanho - 1 - i];
        vetor[tamanho - 1 - i] = temp;
    }
}

//gera um vetor com diferentes, tamanhos, keysize(valores aleatorios) e payloadsize(valores ciclicos), dependendo de KEYSZ, PLSZ, VETSZ em itemT.hpp
void geraVetorControlado(){
    int i, j;
    long long min = static_cast<long long>(std::pow(10, KEYSZ - 1));
    long long max = static_cast<long long>(std::pow(10, KEYSZ)) - 1;

    srand48(1); // semente para geração pseudoaleatória

    for (i = 0; i < VETSZ; i++) {
        vet[i].key = min + static_cast<long long>(drand48() * (max - min + 1));

        // preenche o payload com dígitos cíclicos
        for (j = 0; j < PLSZ - 1; j++) {
            vet[i].payload[j] = '0' + j % 10;
        }
        vet[i].payload[PLSZ - 1] = '\0';
    }
}

//ordena com o algoritmo escolhido pelos argumentos e imprime o relatório
void testaAlgoritmo(OrdenadorUniversal teste, int limiarParticao, int limiarQuebras){
    auto inicio = std::chrono::high_resolution_clock::now();

    teste.escolheAlgoritmo(limiarParticao, limiarQuebras);

    auto fim = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duracao = fim - inicio;
    
    teste.imprimeAnalise();
    std::cout << "Tempo de execução: "<< std::fixed << std::setprecision(4) << duracao.count()*100000 << " microsegundos\n";
}

void AnaliseExperimental() {

    geraVetorControlado();
    int limiarParticao, limiarQuebras, quebras, seed;
    double a, b ,c, limiarCusto;
    estatisticas s;

    //dadosParaRegressao(); //necessário para calcular a,b e c
    a = 0.02043866508;
    b = -0.007342909831;
    c = 0.01509796695;
    limiarCusto = 30.0;
    seed = 1;
    
    OrdenadorUniversal calibracao(vet, VETSZ, limiarCusto, a, b, c, seed);
    limiarParticao = calibracao.determinaLimiarParticao();
    limiarQuebras = calibracao.determinaLimiarQuebra(limiarParticao);

    //quickSort(vet, 0, VETSZ-1, -1, &s); // para teste com vetor ordenado
    //inverterVetor(vet, VETSZ); // para teste com vetor inversamente ordenado
   
    OrdenadorUniversal testeOrdenadorUniversal(vet, VETSZ, limiarCusto, a, b, c, seed);
    OrdenadorUniversal testeQuicksort(vet, VETSZ, limiarCusto, a, b, c, seed);
    OrdenadorUniversal testeInsercao(vet, VETSZ, limiarCusto, a, b, c, seed);


    std::cout << std::endl << "Ordenador Universal";
    testaAlgoritmo(testeOrdenadorUniversal, limiarParticao, limiarQuebras);
    std::cout << std::endl << "QuickSort";
    testaAlgoritmo(testeQuicksort, -1, -1);
    std::cout << std::endl << "Insercao";
    testaAlgoritmo(testeInsercao, -1, VETSZ);
}





