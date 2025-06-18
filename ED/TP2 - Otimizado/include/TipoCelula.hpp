#ifndef TIPO_CELULA_HPP
#define TIPO_CELULA_HPP

#include "Pacote.hpp"

struct InfoAresta {
    double latencia;
    int capacidade;
};

class TipoCelula {
public:
    TipoCelula(){
    pilhaSecao = nullptr;
    proximo = nullptr;
    }

    TipoCelula(PilhaPacotes* pilhaPtr, int capacidade, double latencia){
    this->pilhaSecao = pilhaPtr;
    this->infoAresta.latencia = latencia;
    this->infoAresta.capacidade = capacidade;
    proximo = nullptr;
    }

    PilhaPacotes* pilhaSecao;
    TipoCelula* proximo;
    InfoAresta infoAresta;   
};

#endif