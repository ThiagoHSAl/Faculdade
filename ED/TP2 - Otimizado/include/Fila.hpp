#pragma once
#include <iostream>
#include <stdexcept>

template <typename T>
struct FilaNo {
    T dado;
    FilaNo<T>* proximo;

    FilaNo(T valor) : dado(valor), proximo(nullptr) {}
};

template <typename T>
class Fila {
private:
    FilaNo<T>* primeiro;
    FilaNo<T>* ultimo;
    int tamanho;

public:

    Fila() : primeiro(nullptr), ultimo(nullptr), tamanho(0) {}

    ~Fila() {
        FilaNo<T>* atual = primeiro;
        while (atual != nullptr) {
            FilaNo<T>* proximoTemporario = atual->proximo;
            delete atual;
            atual = proximoTemporario;
        }
    }

     
    Fila(const Fila<T>& other) : primeiro(nullptr), ultimo(nullptr), tamanho(0) {
        FilaNo<T>* noAtualDaOutra = other.primeiro;
        while (noAtualDaOutra != nullptr) {
            this->enfileira(noAtualDaOutra->dado);
            noAtualDaOutra = noAtualDaOutra->proximo;
        }
    }

    Fila<T>& operator=(const Fila<T>& other) {
        if (this == &other) {
            return *this;
        }
        while (!this->estaVazia()) {
            this->desenfileira();
        }

        FilaNo<T>* noAtualDaOutra = other.primeiro;
        while (noAtualDaOutra != nullptr) {
            this->enfileira(noAtualDaOutra->dado);
            noAtualDaOutra = noAtualDaOutra->proximo;
        }
        return *this;
    }

    void enfileira(T item) {
        FilaNo<T>* novo_no = new FilaNo<T>(item);
        if (estaVazia()) {
            primeiro = novo_no;
            ultimo = novo_no;
        } else {
            ultimo->proximo = novo_no;
            ultimo = novo_no;
        }
        tamanho++;
    }

    T desenfileira() {
        if (estaVazia()) {
            throw std::runtime_error("Tentativa de desenfileirar de fila vazia.");
        }
        FilaNo<T>* noDesenfileirado = primeiro;
        T itemDeRetorno = noDesenfileirado->dado;

        primeiro = primeiro->proximo;
        if (primeiro == nullptr) {
            ultimo = nullptr;
        }

        delete noDesenfileirado;
        tamanho--;
        return itemDeRetorno;
    }

    bool contem(T item) const {
        FilaNo<T>* atual = primeiro;
        while (atual != nullptr) {
            if (atual->dado == item) {
                return true;
            }
            atual = atual->proximo;
        }
        return false;
    }

    bool estaVazia() const {
        return tamanho == 0;
    }

    int getTamanho() const {
        return tamanho;
    }

   T getPrimeiro() const {
        if (estaVazia()) {
            throw std::runtime_error("Tentativa de acessar o primeiro elemento de fila vazia.");
        }
        return primeiro->dado;
    }

    FilaNo<T>* getPrimeiroNo() const {
        return primeiro;
    }

    FilaNo<T>* getProximoNo(FilaNo<T>* atual) const {
        if (atual == nullptr) return nullptr;
        return atual->proximo;
    }
};