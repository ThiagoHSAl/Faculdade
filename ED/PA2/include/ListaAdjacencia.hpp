#ifndef LISTAADJACENCIA_HPP
#define LISTAADJACENCIA_HPP
#include "TipoCelula.hpp"

class ListaAdjacencia {
    public:
        ListaAdjacencia();
        ListaAdjacencia(int item);
        ~ListaAdjacencia();

        void Insere(int item);
        void Imprime();
        void Limpa();
        int GetTamanho();
    private:
        TipoCelula* primeiro;
        TipoCelula* ultimo;
        int tamanho;
};

#endif