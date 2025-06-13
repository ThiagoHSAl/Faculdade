#include "ListaEncadeadaRota.hpp"
#include <iostream>
#include <string>

RotaNo::RotaNo(int id) : idArmazem(id), proximo(nullptr) {}

ListaEncadeadaRota::ListaEncadeadaRota() : primeiro(nullptr), ultimo(nullptr), atualNaRota(nullptr), tamanho(0) {
}

ListaEncadeadaRota::~ListaEncadeadaRota() {
    RotaNo* atual = primeiro;
    while (atual != nullptr) {
        RotaNo* proximo = atual->proximo;
        delete atual;
        atual = proximo;
    }
    primeiro = nullptr;
    ultimo = nullptr;
    tamanho = 0;
}

void ListaEncadeadaRota::AdicionaArmazem(int id) {
    RotaNo* novoNo = new RotaNo(id);
    if (primeiro == nullptr) {
        primeiro = novoNo;
        ultimo = novoNo;
        atualNaRota = primeiro;
    } else {
        ultimo->proximo = novoNo;
        ultimo = novoNo;
    }
    tamanho++;
}

void ListaEncadeadaRota::InsereNoInicio(int id) {
    RotaNo* novoNo = new RotaNo(id);
    if (primeiro == nullptr) {
        primeiro = novoNo;
        ultimo = novoNo;
        atualNaRota = primeiro;
    } else {
        novoNo->proximo = primeiro;
        primeiro = novoNo;
        atualNaRota = primeiro;
    }
    tamanho++;
}

int ListaEncadeadaRota::GetProximoArmazem() const {
    if (atualNaRota != nullptr && atualNaRota->proximo != nullptr) {
        return atualNaRota->proximo->idArmazem;
    }
    return -1;
}

void ListaEncadeadaRota::Avanca() {
    if (atualNaRota != nullptr) {
        atualNaRota = atualNaRota->proximo;
    }
}

bool ListaEncadeadaRota::EstaNoFinal() const {
    return atualNaRota == ultimo && ultimo != nullptr;
}

int ListaEncadeadaRota::GetTamanho() const {
    return tamanho;
}

ListaEncadeadaRota::ListaEncadeadaRota(const ListaEncadeadaRota& other) :
    primeiro(nullptr), ultimo(nullptr), atualNaRota(nullptr), tamanho(0) {
    RotaNo* atualOther = other.primeiro;
    while (atualOther != nullptr) {
        AdicionaArmazem(atualOther->idArmazem);
        atualOther = atualOther->proximo;
    }
    if (other.atualNaRota != nullptr) {
        RotaNo* noTemporario = primeiro;
        RotaNo* otherNoTemporario = other.primeiro;
        while (otherNoTemporario != other.atualNaRota && noTemporario != nullptr) {
            otherNoTemporario = otherNoTemporario->proximo;
            noTemporario = noTemporario->proximo;
        }
        atualNaRota = noTemporario;
    } else {
        atualNaRota = nullptr;
    }
}

ListaEncadeadaRota& ListaEncadeadaRota::operator=(const ListaEncadeadaRota& other) {
    if (this != &other) {
        // Limpar lista atual
        RotaNo* atual = primeiro;
        while (atual != nullptr) {
            RotaNo* proximo = atual->proximo;
            delete atual;
            atual = proximo;
        }
        primeiro = nullptr;
        ultimo = nullptr;
        atualNaRota = nullptr;
        tamanho = 0;

        // Copiar elementos da outra lista
        RotaNo* atualOther = other.primeiro;
        while (atualOther != nullptr) {
            AdicionaArmazem(atualOther->idArmazem);
            atualOther = atualOther->proximo;
        }
        // Copiar o estado de atualNaRota após atribuição
        if (other.atualNaRota != nullptr) {
            RotaNo* noTemporario = primeiro;
            RotaNo* otherNoTemporario = other.primeiro;
            while (otherNoTemporario != other.atualNaRota && noTemporario != nullptr) {
                otherNoTemporario = otherNoTemporario->proximo;
                noTemporario = noTemporario->proximo;
            }
            atualNaRota = noTemporario;
        } else {
            atualNaRota = nullptr;
        }
    }
    return *this;
}

RotaNo* ListaEncadeadaRota::GetPrimeiroNo() const {
    return primeiro;
}

RotaNo* ListaEncadeadaRota::GetAtualNaRota() const {
    return atualNaRota;
}

void ListaEncadeadaRota::Imprime() const {
    RotaNo* atual = primeiro;
    while (atual != nullptr) {
        std::cout << atual->idArmazem;
        if (atual->proximo != nullptr) {
            std::cout << " -> ";
        }
        atual = atual->proximo;
    }
    std::cout << std::endl;
}