#include "graph.hpp"

Grafo::Grafo(){
        tamanho = 0;
        vertices = new ListaAdjacencia*[1000];
    
        // inicializa todos os ponteiros como nullptr
        for (int i = 0; i < 1000; i++) {
            vertices[i] = nullptr;
        }
}

Grafo::~Grafo(){
    for(int i = 0; i < tamanho; i++){
        vertices[i]->Limpa();
        delete vertices[i];
    }
}

void Grafo::InsereVertice(){
    vertices[tamanho] = new ListaAdjacencia(tamanho);
    tamanho++;
}

void Grafo::InsereAresta(int v, int w){
    vertices[v]->Insere(w);
}

int Grafo::QuantidadeVertices(){
    return tamanho;
}

int Grafo::QuantidadeArestas(){
    int arestas = 0;
    for(int i = 0; i < tamanho; i++){
        arestas += vertices[i]->GetTamanho();
    }
    return arestas/2;
}

int Grafo::GrauMinimo(){
    int grau = vertices[0]->GetTamanho();
    for(int i = 1; i < tamanho; i++){
        if (grau > vertices[i]->GetTamanho()){
            grau = vertices[i]->GetTamanho();
        }
    }
    return grau;
}

int Grafo::GrauMaximo(){
    int grau = vertices[0]->GetTamanho();
    for(int i = 1; i < tamanho; i++){
        if (grau < vertices[i]->GetTamanho()){
            grau = vertices[i]->GetTamanho();
        }
    }
    return grau;
}

void Grafo::ImprimeVizinhos(int v){
    vertices[v]->Imprime();
}
