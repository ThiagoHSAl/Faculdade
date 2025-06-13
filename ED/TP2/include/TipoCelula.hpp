#ifndef TIPO_CELULA_HPP
#define TIPO_CELULA_HPP

#include "Pacote.hpp"

class TipoCelula {
public:
    TipoCelula(){
    pilhaSecao = nullptr;
    proximo = nullptr;
    }

    TipoCelula(PilhaPacotes* pilhaPtr){
    this->pilhaSecao = pilhaPtr;
    proximo = nullptr;
    }

    PilhaPacotes* pilhaSecao;
    TipoCelula* proximo;  
};

#endif