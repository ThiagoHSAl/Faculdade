#include "Heap.hpp"

Heap::Heap(int maxsize){
    tamanho = 0;
    data = new int[maxsize];
}

Heap::~Heap(){
    delete[] data;
}

void Heap::Inserir(int x){
    int i, posicao, aux;

    data[tamanho] = x;
    i = tamanho;
    posicao = (i - 1) / 2;

    while(data[i] < data[posicao]){
        aux = data[i];
        data[i] = data[posicao];
        data[posicao] = aux;
        i = posicao;
        posicao = (i - 1) / 2;
    }
    tamanho++;
}

int Heap::Remover(){
   
    int removido = data[0];
    data[0] = data[tamanho-1];
    tamanho--;
    
    int i = 0;
    int esquerda, direita, sucessor;

    while(true){
        esquerda = 2*i + 1;
        direita = 2*i + 2;

        // Se ambos os filhos estão fora dos limites, terminamos
        if (esquerda >= tamanho) break;

        if (direita < tamanho && data[direita] < data[esquerda]){
            sucessor = direita;
        } else {
            sucessor = esquerda;
        }

        if (data[i] <= data[sucessor]) break;

        // Troca o nó com o sucessor
        int aux = data[i];
        data[i] = data[sucessor];
        data[sucessor] = aux;

        i = sucessor;
    }

    return removido;
}
