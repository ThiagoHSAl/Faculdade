#include "MinHeapEventos.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>

Evento::Evento(double tempo, TipoEvento tipoEvento, Pacote* pacote, Armazem* armazem) {
    this->tempoOcorrencia = tempo;
    this->tipo = tipoEvento;
    this->pacote = pacote;
    this->armazemAlvo = armazem;
    this->idSecao = -1; 

    std::stringstream stringStream;
    stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo)
       << std::setw(6) << std::setfill('0') << pacote->getIdUnico()
       << "1";
    this->chavePrioridade = stringStream.str();
}

Evento::Evento(double tempo, TipoEvento tipoEvento, Armazem* armazem, int idSecao) {
    this->tempoOcorrencia = tempo;
    this->tipo = tipoEvento;
    this->pacote = nullptr;
    this->armazemAlvo = armazem;
    this->idSecao = idSecao;

    std::stringstream stringStream;
    stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo)
       << std::setw(3) << std::setfill('0') << armazem->GetIdArmazem()
       << std::setw(3) << std::setfill('0') << idSecao
       << "2";
    this->chavePrioridade = stringStream.str();
}

Evento::~Evento() {
    if ((tipo == EVENTO_CHEGADA_INICIAL || tipo == EVENTO_ARMAZENAMENTO) && pacote != nullptr) {
        delete pacote; 
        pacote = nullptr;
    }
}


MinHeapEventos::MinHeapEventos(int cap) : capacidade(cap), tamanhoAtual(0) {
    vetorHeap = new Evento*[capacidade];
}

MinHeapEventos::~MinHeapEventos() {
    for (int i = 0; i < tamanhoAtual; ++i) {
        delete vetorHeap[i];
    }
    delete[] vetorHeap;
}

void MinHeapEventos::heapifyUp(int index) {
    int pai = (index - 1) / 2;
    while (index > 0 && *(vetorHeap[pai]) > *(vetorHeap[index])) {
        Evento* temp = vetorHeap[index];
        vetorHeap[index] = vetorHeap[pai];
        vetorHeap[pai] = temp;
        index = pai;
        pai = (index - 1) / 2;
    }
}

void MinHeapEventos::heapifyDown(int index) {
    int filhoEsquerda = 2 * index + 1;
    int filhoDireita = 2 * index + 2;
    int menor = index;

    if (filhoEsquerda < tamanhoAtual && *(vetorHeap[menor]) > *(vetorHeap[filhoEsquerda])) {
        menor = filhoEsquerda;
    }

    if (filhoDireita < tamanhoAtual && *(vetorHeap[menor]) > *(vetorHeap[filhoDireita])) {
        menor = filhoDireita;
    }

    if (menor != index) {
        Evento* temp = vetorHeap[index];
        vetorHeap[index] = vetorHeap[menor];
        vetorHeap[menor] = temp;
        heapifyDown(menor);
    }
}

void MinHeapEventos::redimensionar() {
    int nova_capacidade = capacidade * 2;
    Evento** novo_array = new Evento*[nova_capacidade];
    for (int i = 0; i < tamanhoAtual; ++i) {
        novo_array[i] = vetorHeap[i];
    }
    delete[] vetorHeap;
    vetorHeap = novo_array;
    capacidade = nova_capacidade;
}

void MinHeapEventos::Insere(Evento* evento) {
    if (tamanhoAtual == capacidade) {
        redimensionar();
    }
    
    vetorHeap[tamanhoAtual] = evento;
    tamanhoAtual++;
    heapifyUp(tamanhoAtual - 1);
}

Evento* MinHeapEventos::ExtraiMin() {
    if (EstaVazia()) {
        return nullptr; 
    }

    Evento* raiz = vetorHeap[0];
    vetorHeap[0] = vetorHeap[tamanhoAtual - 1]; 
    tamanhoAtual--;
    heapifyDown(0); 
    return raiz;
}

bool MinHeapEventos::EstaVazia() const {
    return tamanhoAtual == 0;
}

int MinHeapEventos::GetTamanho() const {
    return tamanhoAtual;
}