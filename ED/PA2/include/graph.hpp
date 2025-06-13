#ifndef GRAPH_HPP
#define GRAPH_HPP

#include "ListaAdjacencia.hpp"
#include <iostream>

struct GrafoVerticeNo {
    ListaAdjacencia *adj_list;
    GrafoVerticeNo *proximo;

    GrafoVerticeNo(ListaAdjacencia *list_ptr) : adj_list(list_ptr), proximo(nullptr) {}
};

class Grafo {
public:
    Grafo();
    ~Grafo();
    void InsereVertice();
    void InsereAresta(int v, int w);
    int QuantidadeVertices();
    int QuantidadeArestas();
    int GrauMinimo();
    int GrauMaximo();
    void ImprimeVizinhos(int v);

private:
    GrafoVerticeNo *primeiro_vertice;
    GrafoVerticeNo *ultimo_vertice;
    int tamanho; // Numero de vértices

    ListaAdjacencia* EncontraVertice(int vertice_id);
};

#endif