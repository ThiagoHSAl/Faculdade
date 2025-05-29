#ifndef HEAP_HPP
#define HEAP_HPP

#include "Aresta.hpp" 

class Heap {
public:
    Heap(int maxsize);
    ~Heap();
    void Inserir(Aresta a);
    Aresta Remover();
    bool Vazio();

private:
    int GetAncestral(int posicao);
    int GetSucessorEsq(int posicao);
    int GetSucessorDir(int posicao);

    int tamanho;   
    int capacidade; 
    Aresta* data;   
};

#endif 

