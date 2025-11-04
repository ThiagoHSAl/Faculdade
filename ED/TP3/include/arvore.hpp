#ifndef ARVORE_HPP
#define ARVORE_HPP


// --- ÁRVORE DE BUSCA BINÁRIA GENÉRICA ---
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
            delete no->valor;
            delete no;
        }
    }

public:
    ArvoreBuscaBinaria() : raiz(nullptr) {}
    
    ~ArvoreBuscaBinaria() {
        // A limpeza completa é delegada ao método limpar() para ser chamada explicitamente,
        // garantindo que o proprietário da árvore controle quando a desalocação profunda acontece.
    }
    
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
};

#endif