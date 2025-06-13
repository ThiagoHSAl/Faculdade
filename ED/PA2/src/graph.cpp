#include "graph.hpp"
#include <limits> 

Grafo::Grafo(){
    tamanho = 0;
    primeiro_vertice = nullptr;
    ultimo_vertice = nullptr;
}

Grafo::~Grafo(){
    GrafoVerticeNo *current = primeiro_vertice;
    while (current != nullptr) {
        GrafoVerticeNo *next = current->proximo;
        delete current->adj_list;
        delete current;          
        current = next;
    }
    primeiro_vertice = nullptr;
    ultimo_vertice = nullptr;
    tamanho = 0;
}

ListaAdjacencia* Grafo::EncontraVertice(int vertice_id) {
    GrafoVerticeNo *current = primeiro_vertice;
    while (current != nullptr) {
        if (current->adj_list->GetVerticeID() == vertice_id) {
            return current->adj_list;
        }
        current = current->proximo;
    }
    return nullptr;
}

void Grafo::InsereVertice(){
    ListaAdjacencia *nova_lista = new ListaAdjacencia(tamanho);
    GrafoVerticeNo *novo_no = new GrafoVerticeNo(nova_lista);

    if (primeiro_vertice == nullptr) {
        primeiro_vertice = novo_no;
        ultimo_vertice = novo_no;
    } else {
        ultimo_vertice->proximo = novo_no;
        ultimo_vertice = novo_no;
    }
    tamanho++;
}

void Grafo::InsereAresta(int v, int w){
    ListaAdjacencia *list_v = EncontraVertice(v);
    if (list_v != nullptr) {
        list_v->Insere(w);
    }
    ListaAdjacencia *list_w = EncontraVertice(w);
    if (list_w != nullptr) {
        list_w->Insere(v);
    }
}

int Grafo::QuantidadeVertices(){
    return tamanho;
}

int Grafo::QuantidadeArestas(){
    int arestas = 0;
    GrafoVerticeNo *current = primeiro_vertice;
    while (current != nullptr) {
        arestas += current->adj_list->GetTamanho();
        current = current->proximo;
    }
    return arestas / 2;
}

int Grafo::GrauMinimo(){
    if (tamanho == 0) {
        return 0; 
    }

    int grau_min = std::numeric_limits<int>::max();
    GrafoVerticeNo *current = primeiro_vertice;
    while (current != nullptr) {
        int current_grau = current->adj_list->GetTamanho();
        if (current_grau < grau_min) {
            grau_min = current_grau;
        }
        current = current->proximo;
    }
    return grau_min;
}

int Grafo::GrauMaximo(){
    if (tamanho == 0) {
        return 0;
    }

    int grau_max = 0; 
    GrafoVerticeNo *current = primeiro_vertice;
    while (current != nullptr) {
        int current_grau = current->adj_list->GetTamanho();
        if (current_grau > grau_max) {
            grau_max = current_grau;
        }
        current = current->proximo;
    }
    return grau_max;
}

void Grafo::ImprimeVizinhos(int v){
    ListaAdjacencia *list_v = EncontraVertice(v);
    if (list_v != nullptr) {
        list_v->Imprime();
    } else {
        std::cout << "Vertice " << v << " nao encontrado." << std::endl;
    }
}