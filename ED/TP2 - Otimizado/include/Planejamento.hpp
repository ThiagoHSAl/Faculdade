#pragma once

#include "Pacote.hpp"
#include "Fila.hpp" 

// Descreve o estado futuro simulado de uma única seção de armazém.
struct SecaoSimulada {
    int idArmazemDono;
    int idSecaoDestino;
    int capacidade;

    PilhaPacotes* pacotesAtuais;   
    PilhaPacotes* pacotesPrevistos;  
    Fila<Pacote*> pacotesEmEspera;  

    SecaoSimulada* proximo;

    SecaoSimulada(int dono, int destino, int cap);
    ~SecaoSimulada();
    int getTamanhoFuturo() const;
    bool temEspaco(int n) const;
};

class PlanejadorDeCiclo {
private:
    SecaoSimulada* primeira;
    SecaoSimulada* ultima;

public:
    PlanejadorDeCiclo();
    ~PlanejadorDeCiclo();

    void AdicionarSecao(int idDono, int idDestino, int capacidade, const PilhaPacotes& pacotesIniciais);
    SecaoSimulada* BuscaSecao(int idDono, int idDestino);
    SecaoSimulada* GetPrimeira() const { return primeira; }
};