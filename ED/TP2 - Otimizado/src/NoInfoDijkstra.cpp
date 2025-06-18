#include "NoInfoDijkstra.hpp"
#include <limits>

ListaInfoDijkstra::ListaInfoDijkstra() : primeiro(nullptr) {}

ListaInfoDijkstra::~ListaInfoDijkstra() {
    NoInfoDijkstra* atual = primeiro;
    while (atual != nullptr) {
        NoInfoDijkstra* proximoTemporario = atual->proximo;
        delete atual;
        atual = proximoTemporario;
    }
    primeiro = nullptr;
}

void ListaInfoDijkstra::AdicionaInfo(int idArmazem) {
    NoInfoDijkstra* novoNo = new NoInfoDijkstra(idArmazem);
    novoNo->proximo = primeiro;
    primeiro = novoNo;
}

NoInfoDijkstra* ListaInfoDijkstra::BuscaInfo(int idArmazem) {
    NoInfoDijkstra* atual = primeiro;
    while (atual != nullptr) {
        if (atual->idArmazem == idArmazem) {
            return atual;
        }
        atual = atual->proximo;
    }
    return nullptr;
}

void ListaInfoDijkstra::Reset() {
    NoInfoDijkstra* atual = primeiro;
    while (atual != nullptr) {
        atual->distancia = std::numeric_limits<int>::max();
        atual->idPredecessor = -1;
        atual->visitado = false;
        atual = atual->proximo;
    }
}