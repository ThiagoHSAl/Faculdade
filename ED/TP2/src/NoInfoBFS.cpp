#include "NoInfoBFS.hpp"
#include <limits>

ListaInfoBFS::ListaInfoBFS() : primeiro(nullptr) {}

ListaInfoBFS::~ListaInfoBFS() {
    NoInfoBFS* atual = primeiro;
    while (atual != nullptr) {
        NoInfoBFS* proximoTemporario = atual->proximo;
        delete atual;
        atual = proximoTemporario;
    }
    primeiro = nullptr;
}

void ListaInfoBFS::AdicionaInfo(int idArmazem) {
    NoInfoBFS* novoNo = new NoInfoBFS(idArmazem);
    novoNo->proximo = primeiro;
    primeiro = novoNo;
}

NoInfoBFS* ListaInfoBFS::BuscaInfo(int idArmazem) {
    NoInfoBFS* atual = primeiro;
    while (atual != nullptr) {
        if (atual->idArmazem == idArmazem) {
            return atual;
        }
        atual = atual->proximo;
    }
    return nullptr;
}

void ListaInfoBFS::Reset() {
    NoInfoBFS* atual = primeiro;
    while (atual != nullptr) {
        atual->distancia = std::numeric_limits<int>::max();
        atual->idPredecessor = -1;
        atual->visitado = false;
        atual = atual->proximo;
    }
}