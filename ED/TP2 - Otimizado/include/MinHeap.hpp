#pragma once
#include <stdexcept>

template <typename T>
class MinHeap {
private:
    T** vetorHeap;
    int capacidade;
    int tamanhoAtual;

    void heapifyUp(int index) {
        int pai = (index - 1) / 2;
        while (index > 0 && *(vetorHeap[pai]) > *(vetorHeap[index])) {
            T* temp = vetorHeap[index];
            vetorHeap[index] = vetorHeap[pai];
            vetorHeap[pai] = temp;
            index = pai;
            pai = (index - 1) / 2;
        }
    }

    void heapifyDown(int index) {
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
            T* temp = vetorHeap[index];
            vetorHeap[index] = vetorHeap[menor];
            vetorHeap[menor] = temp;
            heapifyDown(menor);
        }
    }

    void redimensionar() {
        int nova_capacidade = (capacidade == 0) ? 1 : capacidade * 2;
        T** novo_array = new T*[nova_capacidade];
        for (int i = 0; i < tamanhoAtual; ++i) {
            novo_array[i] = vetorHeap[i];
        }
        delete[] vetorHeap;
        vetorHeap = novo_array;
        capacidade = nova_capacidade;
    }

public:
    MinHeap(int cap = 20) : capacidade(cap), tamanhoAtual(0) {
        vetorHeap = new T*[capacidade];
    }

    // O destrutor limpa todos os ponteiros restantes no heap.
    ~MinHeap() {
        for (int i = 0; i < tamanhoAtual; i++) {
            delete vetorHeap[i];
        }
        delete[] vetorHeap;
    }

    // Assinatura padronizada: sempre insere um ponteiro. O heap assume a posse.
    void Insere(T* novoItem) {
        if (tamanhoAtual == capacidade) {
            redimensionar();
        }
        vetorHeap[tamanhoAtual] = novoItem;
        tamanhoAtual++;
        heapifyUp(tamanhoAtual - 1);
    }

    // Assinatura padronizada: retorna um ponteiro. Transfere a posse para quem chamou.
    T* ExtraiMin() {
        if (EstaVazia()) {
            return nullptr;
        }
        T* raiz = vetorHeap[0];
        vetorHeap[0] = vetorHeap[tamanhoAtual - 1];
        tamanhoAtual--;
        heapifyDown(0);
        return raiz;
    }

    bool EstaVazia() const {
        return tamanhoAtual == 0;
    }

    T* PeekMin() const {
        if (EstaVazia()) {
            return nullptr;
        }
        return vetorHeap[0];
    }
};