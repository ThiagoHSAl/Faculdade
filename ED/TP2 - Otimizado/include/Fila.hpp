#pragma once
#include <iostream>
#include <stdexcept>

// O nó genérico da fila, capaz de armazenar qualquer tipo 'T'.
template <typename T>
struct FilaNo {
    T dado;
    FilaNo<T>* proximo;

    FilaNo(T valor) : dado(valor), proximo(nullptr) {}
};

// A classe de Fila genérica que funciona com qualquer tipo 'T'.
template <typename T>
class Fila {
private:
    FilaNo<T>* primeiro;
    FilaNo<T>* ultimo;
    int tamanho;

public:
    // Construtor
    Fila() : primeiro(nullptr), ultimo(nullptr), tamanho(0) {}

    // Destrutor
    ~Fila() {
        FilaNo<T>* atual = primeiro;
        while (atual != nullptr) {
            FilaNo<T>* proximoTemporario = atual->proximo;
            delete atual;
            atual = proximoTemporario;
        }
    }

     // 1. Construtor de Cópia
    Fila(const Fila<T>& other) : primeiro(nullptr), ultimo(nullptr), tamanho(0) {
        FilaNo<T>* atualOther = other.primeiro;
        while (atualOther != nullptr) {
            this->enfileira(atualOther->dado);
            atualOther = atualOther->proximo;
        }
    }

    // 2. Operador de Atribuição de Cópia
    Fila<T>& operator=(const Fila<T>& other) {
        // Proteção contra auto-atribuição (ex: filaA = filaA)
        if (this == &other) {
            return *this;
        }

        // Limpa a fila atual antes de copiar
        while (!this->estaVazia()) {
            this->desenfileira();
        }

        // Lógica de cópia profunda
        FilaNo<T>* atualOther = other.primeiro;
        while (atualOther != nullptr) {
            this->enfileira(atualOther->dado);
            atualOther = atualOther->proximo;
        }

        return *this;
    }

    // Adiciona um item do tipo T à fila
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

    // Remove e retorna um item do tipo T da fila
    T desenfileira() {
        if (estaVazia()) {
            // Lançar uma exceção é mais seguro do que retornar um valor padrão.
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

    // Verifica se a fila contém um item específico.
    // Requer que o tipo 'T' tenha o operador de igualdade (==) definido.
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
};