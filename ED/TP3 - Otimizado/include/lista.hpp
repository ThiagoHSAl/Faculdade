#ifndef LISTA_HPP
#define LISTA_HPP

#include <cstddef> 
#include <string>
#include <sstream>

// --- LISTA ENCADEADA GENÉRICA ---
template <typename T>
struct NoLista {
    T dado;
    NoLista<T>* proximo;

    NoLista(T d) : dado(d), proximo(nullptr) {}
};

template <typename T>
class Lista {
private:
    NoLista<T>* primeiro;
    NoLista<T>* ultimo;
    int tamanho;

public:
    Lista() : primeiro(nullptr), ultimo(nullptr), tamanho(0) {}

    ~Lista() {
        NoLista<T>* atual = primeiro;
        while (atual != nullptr) {
            NoLista<T>* proximo = atual->proximo;
            delete atual;
            atual = proximo;
        }
    }

    void insereFinal(T dado) {
        NoLista<T>* novoNo = new NoLista<T>(dado);
        if (ultimo == nullptr) {
            primeiro = ultimo = novoNo;
        } else {
            ultimo->proximo = novoNo;
            ultimo = novoNo;
        }
        tamanho++;
    }

    void insereOrdenado(const T& dado) {
        long long novoTimestamp;
        int novoPacoteID;
        std::string placeholderCmd, placeholderTipo;
        std::stringstream ss_novo(dado);
        ss_novo >> novoTimestamp >> placeholderCmd >> placeholderTipo >> novoPacoteID;

        NoLista<T>* novoNo = new NoLista<T>(dado);

        // Caso 1: A lista está vazia.
        if (primeiro == nullptr) {
            primeiro = ultimo = novoNo;
            tamanho++;
            return;
        }

        // Caso 2: Comparar com o primeiro nó para ver se a inserção é no início.
        long long primeiroTimestamp;
        int primeiroPacoteID;
        std::stringstream ss_primeiro(primeiro->dado);
        ss_primeiro >> primeiroTimestamp >> placeholderCmd >> placeholderTipo >> primeiroPacoteID;

        if (novoTimestamp < primeiroTimestamp || (novoTimestamp == primeiroTimestamp && novoPacoteID < primeiroPacoteID)) {
            novoNo->proximo = primeiro;
            primeiro = novoNo;
            tamanho++;
            return;
        }

        // Caso 3: Percorrer a lista para encontrar o ponto de inserção.
        NoLista<T>* atual = primeiro;
        while (atual->proximo != nullptr) {
            long long proximoTimestamp;
            int proximoPacoteID;
            std::stringstream ss_proximo(atual->proximo->dado);
            ss_proximo >> proximoTimestamp >> placeholderCmd >> placeholderTipo >> proximoPacoteID;

            // Critério 1: Tempo
            if (novoTimestamp < proximoTimestamp) {
                break;
            }
            // Critério 2: Desempate por ID do Pacote
            if (novoTimestamp == proximoTimestamp && novoPacoteID < proximoPacoteID) {
                break;
            }
            atual = atual->proximo;
        }

        novoNo->proximo = atual->proximo;
        atual->proximo = novoNo;
        if (novoNo->proximo == nullptr) {
            ultimo = novoNo;
        }
        tamanho++;
    }


    int getTamanho() const {
        return tamanho;
    }

    NoLista<T>* getPrimeiro() const {
        return primeiro;
    }
};

#endif