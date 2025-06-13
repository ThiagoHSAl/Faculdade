#ifndef ESCALONADOR_HPP
#define ESCALONADOR_HPP

#include "MinHeapEventos.hpp"
#include "TopologiaArmazens.hpp"
#include "Transporte.hpp"

class Escalonador {
private:
    MinHeapEventos* filaEventos;
    double relogioSimulacao;
    int pacotesEntreguesCount;
    int totalPacotesInput;

    TopologiaArmazens* topologia;
    Transporte* sistemaTransporte;

    void ExecutaProximoEvento();

public:
    Escalonador(TopologiaArmazens* t, Transporte* tr, int totalPacotes);
    ~Escalonador();

    void AgendarEvento(Evento* evento);
    void InicializaSimulacao(Pacote** todosPacotes, int numeroPacotes);
    void RodaSimulacao();
    void IncrementaPacotesEntregues();
};

#endif