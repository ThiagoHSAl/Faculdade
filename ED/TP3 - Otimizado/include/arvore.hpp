#ifndef ARVORE_HPP
#define ARVORE_HPP

#include "lista.hpp"
#include <cstddef>
#include <string>

// --- NOVO: Estrutura para coletar pares de chave/valor para ordenação ---
template <typename Chave, typename Valor>
struct ParChaveValor {
    Chave chave;
    Valor valor;
};

template <typename Chave, typename Valor>
struct NoArvore {
    Chave chave;
    Valor valor;
    NoArvore<Chave, Valor> *esquerda;
    NoArvore<Chave, Valor> *direita;

    NoArvore(Chave c, Valor v) : chave(c), valor(v), esquerda(nullptr), direita(nullptr) {}
};

template <typename Chave, typename Valor>
class ArvoreBuscaBinaria {
private:
    NoArvore<Chave, Valor>* raiz;

    NoArvore<Chave, Valor>* insereRecursivo(NoArvore<Chave, Valor>* no, Chave chave, Valor valor) {
        if (no == nullptr) {
            return new NoArvore<Chave, Valor>(chave, valor);
        }
        if (chave < no->chave) {
            no->esquerda = insereRecursivo(no->esquerda, chave, valor);
        } else if (chave > no->chave) {
            no->direita = insereRecursivo(no->direita, chave, valor);
        }
        // Se a chave já existe, não faz nada. A atualização é tratada na camada do Gerenciador.
        return no;
    }

    Valor buscaRecursiva(NoArvore<Chave, Valor>* no, Chave chave) {
        if (no == nullptr) {
            return Valor(); // Retorna valor padrão (nullptr para ponteiros)
        }
        if (chave == no->chave) {
            return no->valor;
        }
        if (chave < no->chave) {
            return buscaRecursiva(no->esquerda, chave);
        } else {
            return buscaRecursiva(no->direita, chave);
        }
    }

    void deletaRecursivo(NoArvore<Chave, Valor>* no) {
        if (no != nullptr) {
            deletaRecursivo(no->esquerda);
            deletaRecursivo(no->direita);
            // Deleta o valor apontado (importante para ponteiros)
            delete no->valor;
            delete no;
        }
    }

    // --- NOVO: Função recursiva para busca por intervalo ---
    void buscaIntervaloRecursiva(NoArvore<Chave, Valor>* no, const Chave& inicio, const Chave& fim, Lista<Valor>* resultado) {
        if (no == nullptr) {
            return;
        }
        if (inicio < no->chave) {
            buscaIntervaloRecursiva(no->esquerda, inicio, fim, resultado);
        }
        if (inicio <= no->chave && no->chave <= fim) {
            resultado->insereFinal(no->valor);
        }
        if (no->chave < fim) {
            buscaIntervaloRecursiva(no->direita, inicio, fim, resultado);
        }
    }

    // --- NOVO: Função recursiva para coletar todos os dados em ordem ---
    void emOrdemColetaRecursiva(NoArvore<Chave, Valor>* no, Lista<ParChaveValor<Chave, Valor>>* resultado) {
        if (no == nullptr) {
            return;
        }
        emOrdemColetaRecursiva(no->esquerda, resultado);
        ParChaveValor<Chave, Valor> par = {no->chave, no->valor};
        resultado->insereFinal(par);
        emOrdemColetaRecursiva(no->direita, resultado);
    }

public:
    ArvoreBuscaBinaria() : raiz(nullptr) {}
    ~ArvoreBuscaBinaria() { }
    
    void limpar() {
         deletaRecursivo(raiz);
         raiz = nullptr;
    }

    void insere(Chave chave, Valor valor) {
        raiz = insereRecursivo(raiz, chave, valor);
    }

    Valor busca(Chave chave) {
        return buscaRecursiva(raiz, chave);
    }

    // --- NOVO: Método público para busca por intervalo ---
    Lista<Valor>* buscaIntervalo(const Chave& inicio, const Chave& fim) {
        Lista<Valor>* resultado = new Lista<Valor>();
        buscaIntervaloRecursiva(raiz, inicio, fim, resultado);
        return resultado;
    }

    // --- NOVO: Método público para coletar todos os dados ---
    Lista<ParChaveValor<Chave, Valor>>* emOrdemColeta() {
        Lista<ParChaveValor<Chave, Valor>>* resultado = new Lista<ParChaveValor<Chave, Valor>>();
        emOrdemColetaRecursiva(raiz, resultado);
        return resultado;
    }
};

#endif