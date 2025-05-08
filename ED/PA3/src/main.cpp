#include "Heap.hpp"
#include <iostream>

int main(){
    int maxsize, elemento, i;

    std::cin >> maxsize;
    Heap heap(maxsize);

    for(i = 0; i < maxsize; i++){
        std::cin >> elemento;
        heap.Inserir(elemento);
    }

    for(i = 0; i < maxsize; i++){
        elemento = heap.Remover();
        std::cout << elemento << " ";
    }
}