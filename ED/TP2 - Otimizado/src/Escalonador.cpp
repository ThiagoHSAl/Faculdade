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
                        // Mude o tipo de evento agendado aqui
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
    // 1. Extrai o próximo evento da fila de prioridade.
    Evento* eventoAtual = filaEventos->ExtraiMin();
    if (eventoAtual == nullptr) return;

    relogioSimulacao = eventoAtual->tempoOcorrencia;

    // 2. A lógica principal é dividida: tratamos eventos de PREVISÃO de forma especial.
    if (eventoAtual->tipo == EVENTO_PREVISAO_TRANSPORTE) {
        
        // Se o processo não terminou, executa o planejamento.
        if (pacotesEntreguesCount < totalPacotesInput) {
            
            // 3. CHAMA O PLANEJADOR GLOBAL APENAS UMA VEZ.
            // A função é acionada com os dados do primeiro evento, mas sua lógica interna
            // deve analisar todo o sistema para tomar decisões globais.
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
                    delete filaEventos->ExtraiMin(); // Apenas extrai e deleta.
                } else {
                    break; // Para se o próximo evento for de outro tipo.
                }
            }

            // 5. REAGENDA o próximo ciclo de planejamento global.
            double tempoProximoCiclo = relogioSimulacao + sistemaTransporte->GetIntervaloTransporte();
            AgendarEvento(new Evento(tempoProximoCiclo, EVENTO_PREVISAO_TRANSPORTE, nullptr, -1));
        }
        
    } else {
        // 6. Se for um evento de AÇÃO (não de previsão), processa normalmente.
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

    // 7. Libera a memória do evento que foi processado nesta iteração.
    delete eventoAtual;
}

void Escalonador::RodaSimulacao() {
    while (!filaEventos->EstaVazia()) {
        if (pacotesEntreguesCount >= totalPacotesInput) {
            break;
        }
        /*ImprimeEstadoDaSimulacao();
        std::cout << "\n>>> Pressione ENTER para executar o proximo evento...";
        std::cin.get(); // Pausa a execução e espera o usuário apertar Enter*/
        ExecutaProximoEvento();
    }
}

void Escalonador::IncrementaPacotesEntregues() {
    pacotesEntreguesCount++;
}

void Escalonador::ImprimeEstadoDaSimulacao() const {
    std::cout << "\n=======================================================" << std::endl;
    std::cout << "ESTADO DA SIMULACAO NO TEMPO: " << this->relogioSimulacao << std::endl;
    std::cout << "=======================================================" << std::endl;
    
    // Imprime o estado da Fila de Eventos
    std::cout << "\n--- FILA DE EVENTOS PENDENTES ---" << std::endl;
    if (this->filaEventos->EstaVazia()) {
        std::cout << "  (vazia)" << std::endl;
    } else {
        // Usa a cópia do heap para imprimir sem destruir a fila original
        MinHeap<Evento> copiaHeap = *(this->filaEventos);
        while(!copiaHeap.EstaVazia()) {
            Evento* ev = copiaHeap.ExtraiMin();
            ev->Imprime();
            delete ev; // Deleta a cópia do evento, não o original
        }
    }

    // Imprime o estado dos Armazéns
    std::cout << "\n--- ESTADO DOS ARMAZENS ---" << std::endl;
    TopologiaArmazensVerticeNo* noAtual = this->topologia->primeiroVertice;
    while(noAtual != nullptr) {
        if(noAtual->armazem) {
            std::cout << "Armazem " << noAtual->armazem->GetIdArmazem() << ":" << std::endl;
            if(noAtual->armazem->GetSecoes()){
                noAtual->armazem->GetSecoes()->Imprime();
            }
        }
        noAtual = noAtual->proximo;
    }
    std::cout << "---------------------------------" << std::endl;
}