#ifndef TRANSPORTE_HPP
#define TRANSPORTE_HPP

#include "TopologiaArmazens.hpp"
#include "Pacote.hpp"
#include "Fila.hpp"
#include "ListaEncadeadaRota.hpp"
#include "Evento.hpp"
#include <vector>

class Escalonador;

struct SecaoProcessada {
    PilhaPacotes pacotes;
    Armazem* armazemOrigem;
    int idSecao;
};

class Transporte {
private:
    TopologiaArmazens* topologiaArmazens;
    double custoRemocao;
    double intervaloTransporte;

public:
    Transporte(TopologiaArmazens* t, double custo, double intervalo);
    ~Transporte();

    double GetIntervaloTransporte() const;

    ListaEncadeadaRota CalculaRotaDijkstra(int idOrigem, int idDestino, int idNoProibido = -1);
    bool CalculaEAtribuiRota(Pacote* pacote);
    void CoordenarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, Fila<Pacote*>& pacotesAprovados, double tempoAtual, Escalonador* escalonador);
    void ProcessarRemocao(PilhaPacotes* pilhaParaRemover, PilhaPacotes& pacotesProntos, double tempoAtual, int idArmazem, int idSecao, double& tempoFimRemocao);
    void ProcessarTransporte(PilhaPacotes& pacotesRemovidos, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, Armazem* armazemOrigem, Armazem* armazem_destino, Escalonador* escalonador);
    void ProcessarRearmazenamento(PilhaPacotes* pilhaSecao, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, int idArmazem, int idSecao);
    void ProcessarArmazenamento(Pacote* pacote, Armazem* armazemChegada, double tempoAtual, Escalonador* escalonador);
    void ProcessarEntrega(Pacote* pacote, Armazem* armazemFinal, double tempoAtual, Escalonador* escalonador);
    void ProcessarChegadaInicial(Pacote* pacote, Armazem* armazemInicial, double tempoAtual, Escalonador* escalonador);
    void PlanejarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, double tempoAtual, Escalonador* escalonador);
    PilhaPacotes* EncontraPilhaDoPacote(int id, int& outIdArmazem);

};

#endif