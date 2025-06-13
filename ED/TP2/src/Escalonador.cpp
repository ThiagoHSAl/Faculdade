#include "Escalonador.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>

Escalonador::Escalonador(TopologiaArmazens* t, Transporte* tr, int totalPacotes) :
    topologia(t), sistemaTransporte(tr), totalPacotesInput(totalPacotes) {
    filaEventos = new MinHeapEventos();
    relogioSimulacao = 0.0;
    pacotesEntreguesCount = 0;
}

Escalonador::~Escalonador() {
    delete filaEventos;
}

void Escalonador::AgendarEvento(Evento* evento) {
    filaEventos->Insere(evento);
}

void Escalonador::InicializaSimulacao(Pacote** todosPacotes, int numeroPacotes) {
    double timestamp = todosPacotes[0]->getTimestampPostagem();
    for (int i = 0; i < numeroPacotes; ++i) {
        if (todosPacotes[i]->getTimestampPostagem() < timestamp) {
            timestamp = todosPacotes[i]->getTimestampPostagem();
        }
        Pacote* pacote = todosPacotes[i];

        std::stringstream stringStream;
        stringStream << std::setw(3) << std::setfill('0') << i;
        int novoIdUnico = std::stoi(stringStream.str());
        pacote->setIdUnico(novoIdUnico);
        
        Armazem* armazemOrigem = topologia->GetArmazem(pacote->getArmazemOrigem()); //pacote retorna o ID do Armazem e topologia retorna o objeto Armazem
        AgendarEvento(new Evento(pacote->getTimestampPostagem(), EVENTO_CHEGADA_INICIAL, pacote, armazemOrigem));
    }

    double primeiroTransporte = sistemaTransporte->GetIntervaloTransporte() + timestamp; //simulação começa no instante da primeira postagem
    if (primeiroTransporte > 0) {
        TopologiaArmazensVerticeNo* noAtual = topologia->primeiroVertice;
        while (noAtual != nullptr) {
            Armazem* armazemAtual = noAtual->armazem;
            SecoesArmazem* secoes = noAtual->secoesAdjacentes;
            if (secoes != nullptr) {
                TipoCelula* celulaAtual = secoes->GetPrimeiroCelula();
                while (celulaAtual != nullptr) {
                    if (celulaAtual->pilhaSecao != nullptr) {
                        int idSecao = celulaAtual->pilhaSecao->GetIDEnvio();
                        AgendarEvento(new Evento(primeiroTransporte, EVENTO_INICIA_TRANSPORTE, armazemAtual, idSecao));
                    }
                    celulaAtual = celulaAtual->proximo;
                }
            }
            noAtual = noAtual->proximo;
        }
    }
}

void Escalonador::ExecutaProximoEvento() {
    Evento* proximoEvento = filaEventos->ExtraiMin();
    if (proximoEvento == nullptr) return;

    relogioSimulacao = proximoEvento->tempoOcorrencia;

    switch (proximoEvento->tipo) {
        case EVENTO_CHEGADA_INICIAL:
            sistemaTransporte->ProcessarChegadaInicial(proximoEvento->pacote, proximoEvento->armazemAlvo, relogioSimulacao, this);
            break;
            
        case EVENTO_INICIA_TRANSPORTE:
            if (pacotesEntreguesCount < totalPacotesInput) {
                sistemaTransporte->CoordenarCicloDeTransporte(proximoEvento->armazemAlvo, proximoEvento->idSecao, relogioSimulacao, this);
            
                if (pacotesEntreguesCount < totalPacotesInput) {
                    double tempoProximoCiclo = relogioSimulacao + sistemaTransporte->GetIntervaloTransporte();
                    AgendarEvento(new Evento(tempoProximoCiclo, EVENTO_INICIA_TRANSPORTE, proximoEvento->armazemAlvo, proximoEvento->idSecao));
                }
            }
            break;

        case EVENTO_ARMAZENAMENTO:
            sistemaTransporte->ProcessarArmazenamento(proximoEvento->pacote, proximoEvento->armazemAlvo, relogioSimulacao, this);
            break;
    }

    delete proximoEvento;
}

void Escalonador::RodaSimulacao() {
    while (!filaEventos->EstaVazia()) {
        if (pacotesEntreguesCount >= totalPacotesInput) {
            break;
        }
        ExecutaProximoEvento();
    }
}

void Escalonador::IncrementaPacotesEntregues() {
    pacotesEntreguesCount++;
}