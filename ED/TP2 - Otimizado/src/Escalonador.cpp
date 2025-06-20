#include "Escalonador.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>

Escalonador::Escalonador(TopologiaArmazens* t, Transporte* tr, int totalPacotes) :
    topologia(t), sistemaTransporte(tr), totalPacotesInput(totalPacotes) {
    filaEventos = new MinHeap<Evento>();
    relogioSimulacao = 0.0;
    pacotesEntreguesCount = 0;
}

Escalonador::~Escalonador() {
    delete filaEventos;
}

void Escalonador::AgendarEvento(Evento* evento) {
    filaEventos->Insere(evento);
}

MinHeap<Evento> Escalonador::getCopiaFilaEventos() const {
    return *this->filaEventos;
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

     double primeiroTransporte = sistemaTransporte->GetIntervaloTransporte() + timestamp;
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
                        AgendarEvento(new Evento(primeiroTransporte, EVENTO_PREVISAO_TRANSPORTE, armazemAtual, idSecao));
                    }
                    celulaAtual = celulaAtual->proximo;
                }
            }
            noAtual = noAtual->proximo;
        }
    }
}

void Escalonador::ExecutaProximoEvento() {
    Evento* eventoAtual = filaEventos->ExtraiMin();
    if (eventoAtual == nullptr) return;

    relogioSimulacao = eventoAtual->tempoOcorrencia;

    if (eventoAtual->tipo == EVENTO_PREVISAO_TRANSPORTE) {
        
        if (pacotesEntreguesCount < totalPacotesInput) {
            sistemaTransporte->PlanejarCicloDeTransporte(
                eventoAtual->armazemAlvo,
                eventoAtual->idSecao,
                relogioSimulacao,
                this
            );

            // 4. CONSOME E LIMPA todos os outros eventos de previsão simultâneos.
            // Isso evita que o planejamento seja executado novamente para o mesmo ciclo de tempo.
            while (!filaEventos->EstaVazia() && filaEventos->PeekMin()->tempoOcorrencia == relogioSimulacao) {
                if (filaEventos->PeekMin()->tipo == EVENTO_PREVISAO_TRANSPORTE) {
                    delete filaEventos->ExtraiMin();
                } else {
                    break; 
                }
            }
            double tempoProximoCiclo = relogioSimulacao + sistemaTransporte->GetIntervaloTransporte();
            AgendarEvento(new Evento(tempoProximoCiclo, EVENTO_PREVISAO_TRANSPORTE, nullptr, -1));
        }
        
    } else {
        switch (eventoAtual->tipo) {
            case EVENTO_CHEGADA_INICIAL:
                sistemaTransporte->ProcessarChegadaInicial(eventoAtual->pacote, eventoAtual->armazemAlvo, relogioSimulacao, this);
                break;
            case EVENTO_INICIA_TRANSPORTE:
                sistemaTransporte->CoordenarCicloDeTransporte(
                    eventoAtual->armazemAlvo,
                    eventoAtual->idSecao,
                    eventoAtual->pacotesParaTransportar,
                    relogioSimulacao,
                    this
                );
                break;
            case EVENTO_ARMAZENAMENTO:
                sistemaTransporte->ProcessarArmazenamento(eventoAtual->pacote, eventoAtual->armazemAlvo, relogioSimulacao, this);
                break;
            default:
                break;
        }
    }

    delete eventoAtual;
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
