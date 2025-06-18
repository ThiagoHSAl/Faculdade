#pragma once

#include "Pacote.hpp"
#include "Fila.hpp" // Sua implementação de fila de pacotes

// Descreve o estado futuro simulado de uma única seção de armazém.
struct SecaoSimulada {
    int idArmazemDono;
    int idSecaoDestino;
    int capacidade;

    PilhaPacotes* pacotesAtuais;     // Pacotes que já estão na seção no início do ciclo.
    PilhaPacotes pacotesPrevistos;  // Pacotes que chegarão e caberão na seção.
    Fila<Pacote*> pacotesEmEspera;   // Pacotes que chegarão mas não caberão (FIFO).

    SecaoSimulada* proximo;

    SecaoSimulada(int dono, int destino, int cap);
    int getTamanhoFuturo() const;
    bool temEspaco(int n) const;
};

// Gerencia a lista encadeada de todas as seções simuladas.
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