#include "Heap.hpp" 
#include <stdexcept>          
#include <algorithm>           

Heap::Heap(int maxsize) {
    tamanho = 0;        
    capacidade = maxsize; 
    data = new Aresta[maxsize]; 
}

Heap::~Heap() {
    delete[] data; 
}

int Heap::GetAncestral(int posicao) {
    return (posicao - 1) / 2;
}

int Heap::GetSucessorEsq(int posicao) {
    return 2 * posicao + 1;
}

int Heap::GetSucessorDir(int posicao) {
    return 2 * posicao + 2;
}

void Heap::Inserir(Aresta a) {
    if (tamanho == capacidade) {
        throw std::runtime_error("Heap cheio. Nao eh possivel inserir mais elementos.");
    }

    data[tamanho] = a; 
    int i = tamanho;  
    int ancestral = GetAncestral(i); 

    while (i > 0 && data[i].custo < data[ancestral].custo) {
        std::swap(data[i], data[ancestral]); 
        i = ancestral;                      
        ancestral = GetAncestral(i);        
    }
    tamanho++; 
}

void heapify_down(Aresta* data, int tamanho, int i) {
    int esquerda = 2 * i + 1;
    int direita = 2 * i + 2;
    int menor = i;

    if (esquerda < tamanho && data[esquerda].custo < data[menor].custo) {
        menor = esquerda;
    }
    if (direita < tamanho && data[direita].custo < data[menor].custo) {
        menor = direita;
    }

    if (menor != i) {
        std::swap(data[i], data[menor]);
        heapify_down(data, tamanho, menor);
    }
}

Aresta Heap::Remover() {
    if (Vazio()) {
        throw std::runtime_error("Heap vazio. Nao eh possivel remover elementos.");
    }

    Aresta removido = data[0];     
    data[0] = data[tamanho - 1]; 
    tamanho--;                   

    heapify_down(data, tamanho, 0);

    return removido; 
}

bool Heap::Vazio() {
    return tamanho == 0;
}

