#include "math.h"
#include "AlgoritmosOrdenacao.hpp"
#include "OrdenadorUniversal.hpp"
#include "itemT.hpp"
#include "estatisticas.hpp"
#include <iostream>
#include <iomanip>

//comstrutor da classe
OrdenadorUniversal::OrdenadorUniversal(item_t* v, int t, int custo, double a_, double b_, double c_,int seed){
    this->vetorOriginal = v;  
    this->tamanho = t;        
    this->limiarCusto = custo;
    this->a = a_;
    this->b = b_;
    this->c = c_;
    this-> numeroQuebras = contaQuebras(vetorOriginal, 0, tamanho);
    this->seed = seed;
    resetcounter(&Estatisticas);
    resetCustos(); 
}


int OrdenadorUniversal::getTamanho(int indexador){
    return tamanhosTestados[indexador];
}


int OrdenadorUniversal::menorCusto(){
    int menorCusto = 0;

    for (int i = 1; i < 10; i++){
        if (custosQS[i] < custosQS[menorCusto]){
            menorCusto = i;
        }
    }

    return menorCusto;
}


void OrdenadorUniversal::registraEstatisticas(Algoritmo tipo, int indexador) {
    double custo = a * Estatisticas.cmp + b * Estatisticas.move + c * Estatisticas.calls;
    ((tipo == QUICKSORT) ? custosQS[indexador] = custo : custosIS[indexador] = custo);
}


void OrdenadorUniversal::imprimeEstatisticas(Algoritmo tipo, int indexador) {
    double custo = (tipo == QUICKSORT) ? custosQS[indexador] : custosIS[indexador];

    std::cout << " cost " << std::fixed << std::setprecision(9) << custo
              << " cmp " << Estatisticas.cmp
              << " move " << Estatisticas.move
              << " calls " << Estatisticas.calls << std::endl;
}


void OrdenadorUniversal::resetCustos(){
    for(int i = 0; i < 10; i++){
            custosQS[i] = INFINITY;
            custosIS[i] = INFINITY;
        }
}


item_t* OrdenadorUniversal::copiaVetor(int tamanho){
    item_t* copia = new item_t[tamanho];
    for (int i = 0; i < tamanho; i++)
        copia[i] = vetorOriginal[i];
    return copia; 
}


int OrdenadorUniversal::determinaLimiarParticao(){
    int menorTamanhoParticao = 2;
    int maiorTamanhoParticao = tamanho;
    int indexadorTeste = 0;
    int iteracao = 0;
    int passoTestes = (maiorTamanhoParticao - menorTamanhoParticao) / 5;
    int melhorIndice;
    float diferencaCusto;

    do {
        indexadorTeste = 0;
        std::cout << std::endl << "iter " << iteracao << std::endl;
        resetTamanhosTestados();

        for (int tamanhoParticao = menorTamanhoParticao; tamanhoParticao <= maiorTamanhoParticao; tamanhoParticao  += passoTestes) {
            resetcounter(&Estatisticas);
            tamanhosTestados[indexadorTeste] = tamanhoParticao;

            escolheAlgoritmo(tamanhoParticao, -1);

            std::cout << "mps " << tamanhosTestados[indexadorTeste];
            registraEstatisticas(QUICKSORT, indexadorTeste);
            imprimeEstatisticas(QUICKSORT, indexadorTeste);
            indexadorTeste++;
        }

        melhorIndice = menorCusto();
        calculaNovaFaixa(indexadorTeste, melhorIndice, &menorTamanhoParticao, &maiorTamanhoParticao, &passoTestes);

        diferencaCusto = calculaDiferenca(QUICKSORT, menorTamanhoParticao, maiorTamanhoParticao);
        resetCustos();

        std::cout << "nummps " << indexadorTeste
        << " limParticao " << getTamanho(melhorIndice)
        << " mpsdiff " << std::fixed << std::setprecision(6) << diferencaCusto
        << std::endl;

        iteracao++;
    } while ((diferencaCusto > limiarCusto) && (indexadorTeste >= 5));

    int limiarParticao;
    limiarParticao = getTamanho(melhorIndice);
    return limiarParticao;
}


void OrdenadorUniversal::escolheAlgoritmo(int menorTamanhoParticao, int limiarQuebras){
    item_t* vetorDeTestes;

    vetorDeTestes = copiaVetor(tamanho);

    if (numeroQuebras < limiarQuebras) {
        insercao(vetorDeTestes, 0, tamanho-1, &Estatisticas);
    } else {
        if (tamanho > menorTamanhoParticao) {
            quickSort(vetorDeTestes, 0, tamanho-1, menorTamanhoParticao, &Estatisticas);
        } else {
            insercao(vetorDeTestes, 0, tamanho-1, &Estatisticas);
        }
    }
}


void OrdenadorUniversal::calculaNovaFaixa(int indexadorTeste, int melhorIndice, int* menorTamanhoParticao, int* maiorTamanhoParticao, int* passoTestes) {
    int indexadorNovoMin, indexadorNovoMax;
    if (melhorIndice == 0) {
        indexadorNovoMin = 0;
        indexadorNovoMax = 2;
    } 
    
    else if (melhorIndice == indexadorTeste - 1) {
        indexadorNovoMin = indexadorTeste - 3;
        indexadorNovoMax = indexadorTeste - 1;
    } 
    
    else {
        indexadorNovoMin = melhorIndice - 1;
        indexadorNovoMax = melhorIndice + 1;
    }
    
    *menorTamanhoParticao = getTamanho(indexadorNovoMin);
    *maiorTamanhoParticao = getTamanho(indexadorNovoMax);
    *passoTestes = (*maiorTamanhoParticao - *menorTamanhoParticao) / 5;
    
    if (*passoTestes == 0) {
        *passoTestes = 1;
    }
}


int OrdenadorUniversal::determinaLimiarQuebra(int menorTamanhoParticao){
    int menorLimiarQuebra = 1;
    int maiorLimiarQuebra = tamanho/2;
    int indexadorTeste = 0;
    int iteracao = 0;
    int passoTestes = (maiorLimiarQuebra - menorLimiarQuebra) / 5;
    int melhorIndice;
    float diferencaCusto;
    item_t* vetorDeTestes;

    do {
        indexadorTeste = 0;
        std::cout << std::endl << "iter " << iteracao << std::endl;
        resetTamanhosTestados();

        for (int limiarQuebra = menorLimiarQuebra; limiarQuebra <= maiorLimiarQuebra; limiarQuebra  += passoTestes) {
            resetcounter(&Estatisticas);
            tamanhosTestados[indexadorTeste] = limiarQuebra;

            vetorDeTestes = adicionaQuebras(nullptr, limiarQuebra);
            quickSort(vetorDeTestes, 0, tamanho-1, menorTamanhoParticao, &Estatisticas);

            std::cout << "qs lq " << tamanhosTestados[indexadorTeste];
            registraEstatisticas(QUICKSORT, indexadorTeste);
            imprimeEstatisticas(QUICKSORT, indexadorTeste);

            resetcounter(&Estatisticas);
            vetorDeTestes = adicionaQuebras(nullptr, limiarQuebra);
            insercao(vetorDeTestes, 0, tamanho-1, &Estatisticas);

            std::cout << "in lq " << tamanhosTestados[indexadorTeste];
            registraEstatisticas(INSERCAO, indexadorTeste);
            imprimeEstatisticas(INSERCAO, indexadorTeste);
            indexadorTeste++;
        }

        melhorIndice = menorDiferenca();
        calculaNovaFaixa(indexadorTeste, melhorIndice, &menorLimiarQuebra, &maiorLimiarQuebra, &passoTestes);

        diferencaCusto = calculaDiferenca(INSERCAO, menorLimiarQuebra, maiorLimiarQuebra);
        resetCustos();

        std::cout << "numlq " << indexadorTeste
        << " limQuebras " << getTamanho(melhorIndice)
        << " lqdiff " << std::fixed << std::setprecision(6) << diferencaCusto
        << std::endl;

        iteracao++;
    } while ((diferencaCusto > limiarCusto) && (indexadorTeste >= 5));

    int melhorLimiarQuebra = getTamanho(melhorIndice);
    return melhorLimiarQuebra;
}

item_t* OrdenadorUniversal::adicionaQuebras(item_t* vetor, int quebras){
  vetor = copiaVetor(tamanho);
  quickSort(vetor, 0, tamanho-1, -1, &Estatisticas);
  srand48(seed);
  embaralharVetor(vetor, tamanho, quebras);
  resetcounter(&Estatisticas);
  return vetor;
}

int OrdenadorUniversal::menorDiferenca(){
    int menorDiferenca = 0;

    for (int i = 1; i < 10; i++){
        if (fabs(custosQS[i] - custosIS[i]) < fabs(custosQS[menorDiferenca] - custosIS[menorDiferenca])){
            menorDiferenca = i;
        }
    }

    return menorDiferenca;
}

int OrdenadorUniversal::getIndexadorTamanho(int tamanhoParticao){
    for (int i = 0; i < 10; i++){
        if(this -> tamanhosTestados[i] == tamanhoParticao){
            return i;
        }
    }
    return -1;
}


float OrdenadorUniversal::calculaDiferenca(Algoritmo tipo, int atributoMin, int atributoMax){
    int indexadorMin, indexadorMax;

    indexadorMin = getIndexadorTamanho(atributoMin);
    indexadorMax = getIndexadorTamanho(atributoMax);

    float diferenca = ((tipo == QUICKSORT) ? fabs(custosQS[indexadorMax] - custosQS[indexadorMin]) :
    fabs(custosIS[indexadorMax] - custosIS[indexadorMin]));

    return diferenca;
}


void OrdenadorUniversal::resetTamanhosTestados(){
    for(int i = 0; i < 10; i++){
        tamanhosTestados[i] = -1;
    }
}


void OrdenadorUniversal::imprimeAnalise() {
    double custo = a * Estatisticas.cmp + b * Estatisticas.move + c * Estatisticas.calls; 

    std::cout << std::endl << "cost " << std::fixed << std::setprecision(9) << custo
              << " cmp " << Estatisticas.cmp
              << " move " << Estatisticas.move
              << " calls " << Estatisticas.calls << std::endl;
}