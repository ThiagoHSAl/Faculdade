#include "math.h"
#include "AlgoritmosOrdenacao.hpp"
#include <iostream>
#include <iomanip>

OrdenadorUniversal::OrdenadorUniversal(int* v, int t, int custo, double a_, double b_, double c_){
    this->vetorOriginal = v;  // Inicializando o vetorOriginal
    this->tamanho = t;        // Inicializando o tamanho
    this->limiarCusto = custo;
    this->a = a_;
    this->b = b_;
    this->c = c_;
    this-> numeroQuebras = contaQuebras(vetorOriginal, 0, tamanho);
    resetcounter(&s);
    resetCustos(); 
}

int contaQuebras(int* vetor, int inicio, int final){
    int quantidadeQuebras = 0;
    for(int i = inicio; i < final - 1; i++){
        if(vetor[i] > vetor[i + 1]){
            quantidadeQuebras++;
        }
    }
    return quantidadeQuebras;
}

int OrdenadorUniversal::determinaLimiarParticao(){
    int menorTamanhoParticao = 2;
    int maiorTamanhoParticao = tamanho;
    int indexadorTeste = 0;
    int iteracao = 0;
    int passoTestes = (maiorTamanhoParticao - menorTamanhoParticao) / 5;
    int melhorIndice;
    double diferencaCusto;

    do {
        indexadorTeste = 0;
        std::cout << "iter " << iteracao << std::endl;
        for (int tamanhoParticao = menorTamanhoParticao; tamanhoParticao <= maiorTamanhoParticao; tamanhoParticao  += passoTestes) {
            resetcounter(&s);
            tamanhosTestados[indexadorTeste] = tamanhoParticao;
            escolheAlgoritmo(tamanhoParticao, -1);
            std::cout << "mps " << tamanhosTestados[indexadorTeste];
            registraEstatisticas('q', indexadorTeste);
            imprimeEstatisticas('q', indexadorTeste);
            indexadorTeste++;
        }

        melhorIndice = menorCusto();
        calculaNovaFaixa(indexadorTeste, melhorIndice, &menorTamanhoParticao, &maiorTamanhoParticao, &passoTestes, &diferencaCusto, 'q');
        resetCustos();
        std::cout << "nummps " << indexadorTeste
          << " limParticao " << getTamanho(melhorIndice)
          << " mpsdiff " << std::fixed << std::setprecision(6) << diferencaCusto
          << std::endl;
        iteracao++;
    } while ((diferencaCusto > limiarCusto) && (indexadorTeste >= 6));

    melhorIndice = tamanhosTestados [melhorIndice];
    return melhorIndice;
}

void OrdenadorUniversal::escolheAlgoritmo(int menorTamanhoParticao, int limiarQuebras){
    int* vetorDeTestes;

    vetorDeTestes = copiaVetor(tamanho);

    if (numeroQuebras < limiarQuebras) {
        insercao(vetorDeTestes, 0, tamanho-1, &s);
    } else {
        if (tamanho > menorTamanhoParticao) {
            quickSort(vetorDeTestes, 0, tamanho-1, menorTamanhoParticao, limiarQuebras, &s);
        } else {
            insercao(vetorDeTestes, 0, tamanho-1, &s);
        }
    }
}

void OrdenadorUniversal::calculaNovaFaixa(int indexadorTeste, int melhorIndice, int* menorTamanhoParticao, int* maiorTamanhoParticao, int* passoTestes, double* diferencaCusto, char identificador) {
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
    *diferencaCusto = (identificador == 'q') ? fabs((custosQS[indexadorNovoMax] - custosQS[indexadorNovoMin])) : fabs((custosIS[indexadorNovoMax] - custosIS[indexadorNovoMin]));
    *passoTestes = (*maiorTamanhoParticao - *menorTamanhoParticao) / 5;
    
    if (*passoTestes == 0) {
        *passoTestes = 1;
    }
}


int OrdenadorUniversal::getTamanho(int indexador){
    return tamanhosTestados[indexador];
}


int OrdenadorUniversal::menorCusto(){
    int menorCusto = 0;

    for (int i = 1; i < 6; i++){
        if (custosQS[i] < custosQS[menorCusto]){
            menorCusto = i;
        }
    }

    return menorCusto;
}


void OrdenadorUniversal::registraEstatisticas(char identificador, int indexador){

        if(identificador == 'q'){
            custosQS[indexador] = a * s.cmp + b * s.move + c * s.calls;
        }

        if(identificador == 'i'){
            custosIS[indexador] = a * s.cmp + b * s.move + c * s.calls;
        }
}


void OrdenadorUniversal::imprimeEstatisticas(char identificador, int indexador){
    std::cout << " cost " << std::fixed << std::setprecision(9) << ((identificador == 'q') ? custosQS[indexador] : custosIS[indexador])
              << " cmp " << s.cmp
              << " move " << s.move
              << " calls " << s.calls << std::endl;
}


void OrdenadorUniversal::resetCustos(){
    for(int i = 0; i < 10; i++){
            custosQS[i] = INFINITY;
            custosIS[i] = INFINITY;
        }
}

int* OrdenadorUniversal::copiaVetor(int tamanho){
    int* copia = new int[tamanho];
    for (int i = 0; i < tamanho; i++)
        copia[i] = vetorOriginal[i];
    return copia; // retorna a cópia
}

int OrdenadorUniversal::determinaLimiarQuebra(int particao){
    int menorLimiarQuebra = 1;
    int maiorLimiarQuebra = tamanho/2;
    int indexadorTeste = 0;
    int iteracao = 0;
    int passoTestes = (maiorLimiarQuebra - menorLimiarQuebra) / 5;
    int melhorIndice;
    double diferencaCusto;
    int* vetorDeTestes;

    do {
        indexadorTeste = 0;
        std::cout << "iter " << iteracao << std::endl;
        for (int limiarQuebra = menorLimiarQuebra; limiarQuebra <= maiorLimiarQuebra; limiarQuebra  += passoTestes) {
            resetcounter(&s);
            tamanhosTestados[indexadorTeste] = limiarQuebra;
            vetorDeTestes = vetorComQuebra(vetorDeTestes, limiarQuebra);
            quickSort(vetorDeTestes, 0, tamanho-1, particao, -1, &s);
            std::cout << "qs lq " << tamanhosTestados[indexadorTeste];
            registraEstatisticas('q', indexadorTeste);
            imprimeEstatisticas('q', indexadorTeste);
            resetcounter(&s);
            vetorDeTestes = vetorComQuebra(vetorDeTestes, limiarQuebra);
            insercao(vetorDeTestes, 0, tamanho-1, &s);
            std::cout << "in lq " << tamanhosTestados[indexadorTeste];
            registraEstatisticas('i', indexadorTeste);
            imprimeEstatisticas('i', indexadorTeste);
            indexadorTeste++;
        }

        melhorIndice = menorDiferenca();
        calculaNovaFaixa(indexadorTeste, melhorIndice, &menorLimiarQuebra, &maiorLimiarQuebra, &passoTestes, &diferencaCusto, 'i');
        resetCustos();
        std::cout << "nummlq " << indexadorTeste
          << " limQuebras " << getTamanho(melhorIndice)
          << " lqdiff " << std::fixed << std::setprecision(6) << diferencaCusto
          << std::endl;
        iteracao++;
    } while ((diferencaCusto > limiarCusto) && (indexadorTeste >= 6));

    return melhorIndice;
}

int* OrdenadorUniversal::vetorComQuebra(int* vetor, int quebras){
  vetor = copiaVetor(tamanho);
  quickSort(vetor, 0, tamanho-1, -1, -1, &s);
  srand48(quebras); 
  embaralharVetor(vetor, tamanho, quebras);
  resetcounter(&s);
  return vetor;
}

int OrdenadorUniversal::menorDiferenca(){
    int menorDiferenca = 0;

    for (int i = 1; i < 6; i++){
        if (fabs(custosQS[i] - custosIS[i]) < fabs(custosQS[menorDiferenca] - custosIS[menorDiferenca])){
            menorDiferenca = i;
        }
    }

    return menorDiferenca;
}