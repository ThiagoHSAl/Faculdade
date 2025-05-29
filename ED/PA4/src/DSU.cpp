#include "DSU.hpp" 
#include <iostream>            

DSU::DSU(int n) {
    conjuntos = new int[n]; 
    rank = new int[n];      
    tamanho = n;            
}

DSU::~DSU() {
    delete[] conjuntos; 
    delete[] rank;     
}


void DSU::Make(int x) {
    conjuntos[x] = x; 
    rank[x] = 0;     
}

int DSU::Find(int x) {
    while (conjuntos[x] != x) {
        x = conjuntos[x];
    }
    return x; 
}

void DSU::Union(int x, int y) {
    int raiz_x = Find(x); 
    int raiz_y = Find(y); 

    if (raiz_x != raiz_y) {
        if (rank[raiz_x] < rank[raiz_y]) {
            conjuntos[raiz_x] = raiz_y;
        } else if (rank[raiz_x] > rank[raiz_y]) {
            conjuntos[raiz_y] = raiz_x;
        } else {
            conjuntos[raiz_y] = raiz_x; 
            rank[raiz_x]++;             
        }
    }
}

