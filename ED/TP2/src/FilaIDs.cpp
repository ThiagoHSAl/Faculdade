#include "FilaIDs.hpp"
#include <iostream> 

FilaIDs::FilaIDs() : primeiro(nullptr), ultimo(nullptr), tamanho(0) {}

FilaIDs::~FilaIDs() {
    FilaNo* atual = primeiro;
    while (atual != nullptr) {
        FilaNo* proximoTemporario = atual->proximo;
        delete atual;
        atual = proximoTemporario;
    }
    primeiro = nullptr;
    ultimo = nullptr;
    tamanho = 0;
}

void FilaIDs::enfileira(int id) {
    FilaNo* novo_no = new FilaNo(id);
    if (estaVazia()) {
        primeiro = novo_no;
        ultimo = novo_no;
    } else {
        ultimo->proximo = novo_no;
        ultimo = novo_no;
    }
    tamanho++;
}

int FilaIDs::desenfileira() {
    if (estaVazia()) {
        std::cerr << "Erro: Tentativa de desenfileirar de fila vazia." << std::endl;
        return -1;
    }
    FilaNo* noDesenfileirado = primeiro;
    int idRetorno = noDesenfileirado->id;
    primeiro = primeiro->proximo;
    if (primeiro == nullptr) {
        ultimo = nullptr;
    }
    delete noDesenfileirado;
    tamanho--;
    return idRetorno;
}

bool FilaIDs::estaVazia() const {
    return tamanho == 0;
}

int FilaIDs::getTamanho() const {
    return tamanho;
}