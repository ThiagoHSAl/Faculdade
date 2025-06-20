#include "Transporte.hpp"
#include "Escalonador.hpp"
#include "Fila.hpp"
#include "NoInfoDijkstra.hpp"
#include "MinHeap.hpp"
#include "Evento.hpp"
#include "Planejamento.hpp"
#include "TopologiaArmazens.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <limits>


// --- FUNÇÕES DE FORMATAÇÃO DE SAÍDA ---
static std::string armazemESecaoFormatado(int id1, int id2) {
    std::stringstream stringStream;
    stringStream << std::setw(3) << std::setfill('0') << id1 
       << " na secao " << std::setw(3) << std::setfill('0') << id2;
    return stringStream.str();
}

static std::string origemEDestinoFormatado(int id1, int id2) {
    std::stringstream stringStream;
    stringStream << "de " << std::setw(3) << std::setfill('0') << id1 
       << " para " << std::setw(3) << std::setfill('0') << id2;
    return stringStream.str();
}

static void imprimirLinhaFormatada(double tempo, int idPacote, const std::string& acao, const std::string& detalhes) {
    std::cout << std::setw(7) << std::setfill('0') << static_cast<long long int>(tempo)
              << " pacote " << std::setw(3) << std::setfill('0') << idPacote 
              << " " << acao << " " << detalhes << std::endl;
}

// --- MÉTODOS DA CLASSE TRANSPORTE ---
Transporte::Transporte(TopologiaArmazens* t, double custo, double intervalo, int capSecao) {
    topologiaArmazens = t;
    custoRemocao = custo;
    intervaloTransporte = intervalo;
    capacidadeSecaoArmazenamento = capSecao; 
}


Transporte::~Transporte() {}


double Transporte::GetIntervaloTransporte() const {
    return intervaloTransporte;
}


void Transporte::CoordenarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, Fila<Pacote*>& pacotesAprovados, double tempoAtual, Escalonador* escalonador) {
    if (!armazemOrigem || pacotesAprovados.estaVazia()) {
        return;
    }
    
    PilhaPacotes* pilhaReal = armazemOrigem->GetSecao(idSecao);
    if (!pilhaReal) return;

    PilhaPacotes pacotesParaTransportar;

    // 2. Itera sobre a "ordem de serviço" (pacotes aprovados pelo planejador).
    while (!pacotesAprovados.estaVazia()) {
        Pacote* pacoteAprovado = pacotesAprovados.desenfileira();
        if (pacoteAprovado) {
            Pacote* pacoteRemovido = pilhaReal->RemovePacotePorId(pacoteAprovado->getIdUnico());
            
            if (pacoteRemovido) {
                pacotesParaTransportar.empilhaPacote(pacoteRemovido);
            }
        }
    }

    if (pacotesParaTransportar.estaVazia()) {
        return;
    }
    
    PilhaPacotes pacotesProntosParaTransporte;
    PilhaPacotes pacotesSobraram;
    double tempoFimRemocao = tempoAtual;

    // Passa os pacotes para o "empacotador"
    ProcessarRemocao(&pacotesParaTransportar, pacotesProntosParaTransporte, tempoAtual, armazemOrigem->GetIdArmazem(), idSecao, tempoFimRemocao);
    
    // Passa os pacotes prontos para o "carregador"
    Armazem* armazemDestino = topologiaArmazens->GetArmazem(idSecao);
    ProcessarTransporte(pacotesProntosParaTransporte, pacotesSobraram, tempoFimRemocao, armazemOrigem, armazemDestino, escalonador);

    // Passa as sobras para o "repositor"
    ProcessarRearmazenamento(pilhaReal, pacotesSobraram, tempoFimRemocao, armazemOrigem->GetIdArmazem(), idSecao);
}


void Transporte::ProcessarRemocao(PilhaPacotes* pilhaParaRemover, PilhaPacotes& pacotesProntos, double tempoAtual, int idArmazem, int idSecao, double& tempoFimRemocao) {
    tempoFimRemocao = tempoAtual;

    PilhaPacotes pilhaInvertida;
    while(!pilhaParaRemover->estaVazia()){
        pilhaInvertida.empilhaPacote(pilhaParaRemover->desempilhaPacote());
    }

    while (!pilhaInvertida.estaVazia()) {
        Pacote* pacote = pilhaInvertida.desempilhaPacote();
        tempoFimRemocao += custoRemocao;

        double duracaoEstadia = tempoFimRemocao - pacote->getTempoEntradaArmazemAtual();
        pacote->setTempoArmazenado(pacote->getTempoArmazenado() + duracaoEstadia);

        std::string qualArmazemQualSecao = armazemESecaoFormatado(idArmazem, idSecao);
        imprimirLinhaFormatada(tempoFimRemocao, pacote->getIdUnico(), "removido de", qualArmazemQualSecao);
        pacote->setEstadoAtual(REMOVIDO);

        pacotesProntos.empilhaPacote(pacote);
    }
}


void Transporte::ProcessarTransporte(PilhaPacotes& pacotesProntos, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, Armazem* armazemOrigem, Armazem* armazemDestino, Escalonador* escalonador) {
    int pacotesEnviados = 0;
    int capacidadeDaRota = topologiaArmazens->GetCapacidadeAresta(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());

    while (!pacotesProntos.estaVazia()) {
        Pacote* pacote = pacotesProntos.desempilhaPacote();

        if (pacotesEnviados < capacidadeDaRota) {
           int idPacote = pacote->getIdUnico();
            std::string deOndeparaOnde = origemEDestinoFormatado(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());
            imprimirLinhaFormatada(tempoFimRemocao, idPacote, "em transito", deOndeparaOnde);

            pacote->setEstadoAtual(CHEGADA_ESCALONADA);
            pacote->setTempoInicioTransito(tempoFimRemocao);
            double latenciaDaRota = topologiaArmazens->GetLatenciaAresta(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());
            double tempoChegada = tempoFimRemocao + latenciaDaRota;

            escalonador->AgendarEvento(new Evento(tempoChegada, EVENTO_ARMAZENAMENTO, new Pacote(*pacote), armazemDestino));
            pacotesEnviados++;
        } else {
            // O caminhão está cheio, este pacote sobra
            pacotesSobraram.empilhaPacote(pacote);
        }
    }
}


void Transporte::ProcessarRearmazenamento(PilhaPacotes* pilhaSecao, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, int IdArmazem, int idSecao) {
    PilhaPacotes pilhaRearmazenamento;

    while(!pacotesSobraram.estaVazia()){
        pilhaRearmazenamento.empilhaPacote(pacotesSobraram.desempilhaPacote());
    }

    while (!pilhaRearmazenamento.estaVazia()) {
        Pacote* pacote = pilhaRearmazenamento.desempilhaPacote();

        pacote->setTempoEntradaArmazemAtual(tempoFimRemocao);
        pacote->setEstadoAtual(ARMAZENADO);

        pilhaSecao->empilhaPacote(pacote);

        std::string qualArmazemQualSecao = armazemESecaoFormatado(IdArmazem, idSecao);
        int idPacote = pacote->getIdUnico();
        imprimirLinhaFormatada(tempoFimRemocao, idPacote, "rearmazenado em", qualArmazemQualSecao);
    }
}


void Transporte::ProcessarArmazenamento(Pacote* pacote, Armazem* armazemChegada, double tempoAtual, Escalonador* escalonador) {
    if (!pacote || !armazemChegada){
        return;
    } 

    if(pacote->getEstadoAtual() == CHEGADA_ESCALONADA){
        pacote->setTempoFimTransito(tempoAtual);
        double duracaoTransito = pacote->getTempoFimTransito() - pacote->getTempoInicioTransito();
        pacote->setTempoEmTransito(pacote->getTempoEmTransito() + duracaoTransito);
    }

    pacote->avancaNaRota(); 
    if (pacote->chegouAoDestinoFinal()) {
        ProcessarEntrega(pacote, armazemChegada, tempoAtual, escalonador);
    } 
    
    else {
        pacote->setEstadoAtual(ARMAZENADO);
        pacote->setTempoEntradaArmazemAtual(tempoAtual);

        int idSecao = pacote->getProximoArmazemNaRota();
        armazemChegada->ArmazenaPacote(pacote, idSecao);
        int idArmazemChegada = armazemChegada->GetIdArmazem();
        std::string qualArmazemQualSecao = armazemESecaoFormatado(idArmazemChegada, idSecao);
        int idPacote = pacote->getIdUnico();
        imprimirLinhaFormatada(tempoAtual, idPacote, "armazenado em", qualArmazemQualSecao);
    }
}


void Transporte::ProcessarEntrega(Pacote* pacote, Armazem* armazemFinal, double tempoAtual, Escalonador* escalonador) {
    if (!pacote || !armazemFinal){
        return;
    } 

    PilhaPacotes* destinoFinal;
    destinoFinal = armazemFinal->GetDestinoFinal();
    destinoFinal->empilhaPacote(pacote);
    pacote->setEstadoAtual(ENTREGUE);

    std::stringstream armazemFinalFormatado;
    int idpacote = pacote->getIdUnico();
    armazemFinalFormatado << std::setw(3) << std::setfill('0') << armazemFinal->GetIdArmazem();
    imprimirLinhaFormatada(tempoAtual, idpacote, "entregue em", armazemFinalFormatado.str());

    if (escalonador) { 
        escalonador->IncrementaPacotesEntregues();
    }
}

void Transporte::ProcessarChegadaInicial(Pacote* pacote, Armazem* armazemInicial, double tempoAtual, Escalonador* escalonador) {
    if (!pacote || !armazemInicial){
        return;
    } 

    if (pacote->getRota() == nullptr || pacote->getRota()->GetTamanho() == 0) {
        CalculaEAtribuiRota(pacote);
    }

    if (pacote->chegouAoDestinoFinal()) {
        ProcessarEntrega(pacote, armazemInicial, tempoAtual, escalonador);
        return;
    }

    int idProximoArmazem = pacote->getProximoArmazemNaRota();
    if (idProximoArmazem == -1) {
        ProcessarEntrega(pacote, armazemInicial, tempoAtual, escalonador);
        return;
    }

    pacote->setEstadoAtual(ARMAZENADO);
    pacote->setTempoEntradaArmazemAtual(tempoAtual);

    armazemInicial->ArmazenaPacote(pacote, idProximoArmazem);

    int idArmazemChegada = armazemInicial->GetIdArmazem();
    int idSecao = pacote->getProximoArmazemNaRota();
    std::string qualArmazemQualSecao = armazemESecaoFormatado(idArmazemChegada, idSecao);
    int idPacote = pacote->getIdUnico();
    imprimirLinhaFormatada(tempoAtual, idPacote, "armazenado em", qualArmazemQualSecao);
}

// --- Métodos Utilitários ---
ListaEncadeadaRota Transporte::CalculaRotaDijkstra(int idOrigem, int idDestino, int idNoProibido) {
    if (topologiaArmazens == nullptr) {
        return ListaEncadeadaRota();
    }
    if (idOrigem == idNoProibido || idDestino == idNoProibido) {
        return ListaEncadeadaRota();
    }

    ListaInfoDijkstra infoNos;
    TopologiaArmazensVerticeNo* noAtualGrafo = topologiaArmazens->primeiroVertice;
    while (noAtualGrafo != nullptr) {
        infoNos.AdicionaInfo(noAtualGrafo->armazem->GetIdArmazem());
        noAtualGrafo = noAtualGrafo->proximo;
    }

    infoNos.Reset();

    NoInfoDijkstra* infoOrigem = infoNos.BuscaInfo(idOrigem);
    if (infoOrigem != nullptr) {
        infoOrigem->distancia = 0;
    }

    MinHeap<NoHeapDijkstra> filaPrioridade;
    filaPrioridade.Insere(new NoHeapDijkstra(idOrigem, 0));

    while (!filaPrioridade.EstaVazia()) {
        NoHeapDijkstra* noAtual = filaPrioridade.ExtraiMin();
        int idU = noAtual->idArmazem;

        NoInfoDijkstra* infoU = infoNos.BuscaInfo(idU);
        if (infoU == nullptr || infoU->visitado) {
            delete noAtual; 
            continue;
        }
        infoU->visitado = true; 

        if (idU == idDestino) {
            delete noAtual;
            break;
        }

        SecoesArmazem* secoesU = topologiaArmazens->GetSecoesArmazem(idU);
        if (secoesU != nullptr) {
            TipoCelula* celulaVizinho = secoesU->GetPrimeiroCelula();
            while (celulaVizinho != nullptr) {
                int idVizinhoV = celulaVizinho->pilhaSecao->GetIDEnvio();
                
                if (idVizinhoV == idNoProibido) {
                    celulaVizinho = celulaVizinho->proximo;
                    continue;
                }

                double latenciaAresta = celulaVizinho->infoAresta.latencia;
                NoInfoDijkstra* infoV = infoNos.BuscaInfo(idVizinhoV);

                if (infoV != nullptr && !infoV->visitado && (infoU->distancia + latenciaAresta < infoV->distancia)) {
                    infoV->distancia = infoU->distancia + latenciaAresta;
                    infoV->idPredecessor = idU;
                    filaPrioridade.Insere(new NoHeapDijkstra(idVizinhoV, infoV->distancia));
                }
                celulaVizinho = celulaVizinho->proximo;
            }
        }
        delete noAtual; 
    }
    NoInfoDijkstra* infoDestino = infoNos.BuscaInfo(idDestino);
    if (infoDestino == nullptr || infoDestino->distancia == std::numeric_limits<int>::max()) {
        return ListaEncadeadaRota();
    }

    ListaEncadeadaRota rotaResultante;
    int idNoAtualRota = idDestino; 

    // Loop para reconstruir a rota de trás para frente, do destino à origem
    while (true) { 
        NoInfoDijkstra* infoAtual = infoNos.BuscaInfo(idNoAtualRota);

        if (infoAtual == nullptr || (infoAtual->idPredecessor == -1 && idNoAtualRota != idOrigem)) {
            return ListaEncadeadaRota();
        }

        rotaResultante.InsereNoInicio(idNoAtualRota);

        if (idNoAtualRota == idOrigem) {
            break;
        }
        idNoAtualRota = infoAtual->idPredecessor;
    }

    // --- Verificações Finais de Consistência da Rota Reconstruída ---
    if (rotaResultante.GetTamanho() == 0) {
        return ListaEncadeadaRota();
    }
    
    if (rotaResultante.GetPrimeiroNo()->idArmazem != idOrigem) {
        return ListaEncadeadaRota();
    }
        if (rotaResultante.GetTamanho() == 1 && idOrigem != idDestino) {
        return ListaEncadeadaRota(); 
    }

    return rotaResultante;
}

bool Transporte::CalculaEAtribuiRota(Pacote* pacote) {
    if (pacote == nullptr) {
        return false;
    }
    ListaEncadeadaRota rota_calculada = CalculaRotaDijkstra(pacote->getArmazemOrigem(), pacote->getArmazemDestino());

    if (rota_calculada.GetTamanho() > 0) {
        pacote->setRota(new ListaEncadeadaRota(rota_calculada));
        return true;
    } else {
        return false;
    }
}

PilhaPacotes* Transporte::EncontraPilhaDoPacote(int id, int& outIdArmazem) {
    TopologiaArmazensVerticeNo* noBusca = topologiaArmazens->primeiroVertice;
    while(noBusca != nullptr) {
        SecoesArmazem* secoes = noBusca->armazem->GetSecoes();
        if (!secoes) { return nullptr; }
        TipoCelula* celula = secoes->GetPrimeiroCelula();
        while(celula != nullptr) {
            PilhaPacotes* secaoReal = celula->pilhaSecao;
            if(!secaoReal) {  return nullptr;  }
            PilhaPacotesNode* p_node_atual = secaoReal->getPrimeiroNode();
            while(p_node_atual != nullptr) {
                if (p_node_atual->pacote != nullptr && p_node_atual->pacote->getIdUnico() == id) {
                    outIdArmazem = noBusca->armazem->GetIdArmazem();
                    return secaoReal; 
                }
                p_node_atual = secaoReal->getProximoNode(p_node_atual);
            }
            celula = celula->proximo;
        }
        noBusca = noBusca->proximo;
    }
    return nullptr; 
}

void Transporte::PlanejarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, double tempoAtual, Escalonador* escalonador) {
    /*Esta verificação garante que a lógica de planejamento global só rode uma vez por ciclo,
     acionada pelo primeiro evento de previsão que for processado.*/
    static double ultimoTempoPlanejado = -1.0;
    if (tempoAtual == ultimoTempoPlanejado) {
        return; 
    }
    ultimoTempoPlanejado = tempoAtual;

    // --- PASSO A: INICIALIZAR O AMBIENTE DE SIMULAÇÃO ---
    PlanejadorDeCiclo planejador;
    TopologiaArmazensVerticeNo* noSetup = topologiaArmazens->primeiroVertice;
    while(noSetup != nullptr) {
        SecoesArmazem* secoesReais = noSetup->armazem->GetSecoes();
        if(secoesReais) {
            TipoCelula* celulaReal = secoesReais->GetPrimeiroCelula();
            while(celulaReal != nullptr) {
                if(celulaReal->pilhaSecao) {
                    planejador.AdicionarSecao(noSetup->armazem->GetIdArmazem(),
                                             celulaReal->pilhaSecao->GetIDEnvio(),
                                             this->capacidadeSecaoArmazenamento,
                                             *celulaReal->pilhaSecao);
                }
                celulaReal = celulaReal->proximo;
            }
        }
        noSetup = noSetup->proximo;
    }
    
    // --- PASSO B: COLETAR E ORDENAR OS MOVIMENTOS POR PRIORIDADE ---
    MinHeap<PacoteComPrevisao> pacotesOrdenadosPorChegada;
    
    TopologiaArmazensVerticeNo* noBusca = topologiaArmazens->primeiroVertice;
    while(noBusca != nullptr) {
        SecoesArmazem* secoes = noBusca->armazem->GetSecoes();
        if (secoes) {
            TipoCelula* celula = secoes->GetPrimeiroCelula();
            while(celula != nullptr) {
                PilhaPacotes* secaoReal = celula->pilhaSecao;
                if(secaoReal && !secaoReal->estaVazia()){
                    
                    // 1. Calcula o tempo de partida para o grupo INTEIRO desta seção.
                    double tempoDePartidaDaSecao = tempoAtual + (secaoReal->getTamanho() * this->custoRemocao);
                    double latencia = topologiaArmazens->GetLatenciaAresta(noBusca->armazem->GetIdArmazem(), celula->pilhaSecao->GetIDEnvio());
                    double tempoChegada = tempoDePartidaDaSecao + latencia;
                    Pacote* pacoteAtualNaPilha = secaoReal->getPrimeiro(); 
                    while(pacoteAtualNaPilha != nullptr){
                        pacotesOrdenadosPorChegada.Insere(new PacoteComPrevisao(pacoteAtualNaPilha, tempoChegada, noBusca->armazem->GetIdArmazem()));
                        pacoteAtualNaPilha = secaoReal->ObterProximoPacote(pacoteAtualNaPilha);
                    }
                }
                celula = celula->proximo;
            }
        }
        noBusca = noBusca->proximo;
    }


    // --- NOVO PASSO B.2: CRIAR MANIFESTO DE PARTIDAS ---
    struct ManifestoPartida {
        int idArmazem;
        int idSecao;
        int contagemSaidas = 0;
        ManifestoPartida* proximo = nullptr;
    };
    ManifestoPartida* primeiroManifesto = nullptr;

    MinHeap<PacoteComPrevisao> copiaHeap = pacotesOrdenadosPorChegada; 
    while(!copiaHeap.EstaVazia()) {
        PacoteComPrevisao* previsao = copiaHeap.ExtraiMin();
        
        int idOrigem = previsao->armazemOrigemTransporte;
        int idDestino = previsao->pacote->getProximoArmazemNaRota(); 

        // Encontra ou cria o manifesto para esta seção de partida
        ManifestoPartida* manifesto = primeiroManifesto;
        while(manifesto != nullptr) {
            if(manifesto->idArmazem == idOrigem && manifesto->idSecao == idDestino) break;
            manifesto = manifesto->proximo;
        }
        if(manifesto == nullptr) {
            manifesto = new ManifestoPartida();
            manifesto->idArmazem = idOrigem;
            manifesto->idSecao = idDestino;
            manifesto->proximo = primeiroManifesto;
            primeiroManifesto = manifesto;
        }
        manifesto->contagemSaidas++;
        delete previsao;
    }

    // --- PASSO C: SIMULAR FLUXO LÍQUIDO USANDO O MANIFESTO ---
    // Processa os pacotes ordenados por tempo de chegada previsto para simular congestionamento.
    while(!pacotesOrdenadosPorChegada.EstaVazia()) {
        PacoteComPrevisao* chegada = pacotesOrdenadosPorChegada.ExtraiMin(); 

        if (chegada->pacote == nullptr || chegada->pacote->getRota() == nullptr) {
            delete chegada;
            continue;
        }

        int idArmazemDonoSecao = chegada->armazemOrigemTransporte; 
        int idSecaoDestinoSecao = chegada->pacote->getProximoArmazemNaRota(); 

        /*Se o próximo destino é -1, significa que o pacote chegaria ao seu destino final nesta etapa simulada.  Nesses casos, ele não ocuparia uma seção de saída.*/
        if (idSecaoDestinoSecao == -1) { 
            delete chegada;
            continue;
        }
        SecaoSimulada* secaoSimuladaAlvo = planejador.BuscaSecao(idArmazemDonoSecao, idSecaoDestinoSecao);
        if (secaoSimuladaAlvo) {
            // O manifesto conta as intenções de saída para todas as rotas/seções.
            int numSaindoRealPrevisto = 0; 
            ManifestoPartida* manifestoBusca = primeiroManifesto;
            while(manifestoBusca != nullptr){
                if(manifestoBusca->idArmazem == idArmazemDonoSecao && manifestoBusca->idSecao == idSecaoDestinoSecao){
                    numSaindoRealPrevisto = manifestoBusca->contagemSaidas;
                    break;
                }
                manifestoBusca = manifestoBusca->proximo;
            }

            int capacidadeTransporteDaRota = topologiaArmazens->GetCapacidadeAresta(idArmazemDonoSecao, idSecaoDestinoSecao);

            // Calcula o número efetivo de pacotes que realmente conseguirão sair da seção, limitado pela capacidade do caminhão.
            int numSaindoEfetivo = std::min(numSaindoRealPrevisto, capacidadeTransporteDaRota); 
            int ocupacaoInicial = secaoSimuladaAlvo->pacotesAtuais->getTamanho(); 
            int aprovadosParaSairNestaSimulacao = secaoSimuladaAlvo->pacotesPrevistos->getTamanho(); 
            
            int ocupacaoFuturaDaFilaDeSaida = secaoSimuladaAlvo->pacotesPrevistos->getTamanho() + 1;

            // Verifica se a ocupação prevista excede a capacidade de armazenamento da seção.
            if (ocupacaoFuturaDaFilaDeSaida <= secaoSimuladaAlvo->capacidade) {
                secaoSimuladaAlvo->pacotesPrevistos->empilhaPacote(chegada->pacote); 
            } else {
                // Gargalo real detectado: mesmo com as saídas, não haverá espaço para este pacote.
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << chegada->pacote->getIdUnico() 
                          << " Congestionamento previsto na secao " 
                          << armazemESecaoFormatado(idArmazemDonoSecao, idSecaoDestinoSecao)
                          << " (Ocupacao: " << ocupacaoFuturaDaFilaDeSaida 
                          << ", Capacidade: " << secaoSimuladaAlvo->capacidade << ")" << std::endl;
                secaoSimuladaAlvo->pacotesEmEspera.enfileira(chegada->pacote); 
            }
        }
        
        delete chegada; 
    }

    ManifestoPartida* manifestoAtual = primeiroManifesto;
    while(manifestoAtual != nullptr) {
        ManifestoPartida* proximo = manifestoAtual->proximo;
        delete manifestoAtual;
        manifestoAtual = proximo;
    }

    // --- PASSO D: ANALISAR PACOTES EM ESPERA E REMANEJAR IMEDIATAMENTE ---
    
    Fila<int> idsParaEspera;

    SecaoSimulada* secaoSimuladaAtual = planejador.GetPrimeira();
    while (secaoSimuladaAtual != nullptr) {
        Fila<Pacote*> copiaEspera = secaoSimuladaAtual->pacotesEmEspera;
        while (!copiaEspera.estaVazia()) {
            Pacote* p = copiaEspera.desenfileira();
            ListaEncadeadaRota novaRota = CalculaRotaDijkstra(secaoSimuladaAtual->idArmazemDono, p->getArmazemDestino(), secaoSimuladaAtual->idSecaoDestino);

            // --- Início do Bloco de Decisão Refatorado ---
            if (novaRota.GetTamanho() <= 1) {
                idsParaEspera.enfileira(p->getIdUnico());
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << p->getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Nenhuma rota alternativa viavel encontrada." << std::endl;
                continue; 
            }
            double latenciaNova = novaRota.CalculaLatenciaTotal(topologiaArmazens);
            double latenciaAntigaRestante = p->getRota()->CalculaLatenciaRestante(topologiaArmazens);

            if (latenciaNova > latenciaAntigaRestante + GetIntervaloTransporte()) {
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " <<  std::setw(3) << std::setfill('0') << p->getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Rota alternativa e muito longa (Latencia: " << latenciaNova << ")." << std::endl;
                idsParaEspera.enfileira(p->getIdUnico());
                continue; 
            }

            // Se chegou aqui, a latência é aceitável. Vamos verificar a capacidade do novo destino.
            RotaNo* primeiroNoDaNovaRota = novaRota.GetPrimeiroNo();
            if (primeiroNoDaNovaRota == nullptr || primeiroNoDaNovaRota->proximo == nullptr) {
                idsParaEspera.enfileira(p->getIdUnico());
                continue;
            }
            int idNovaOrigem = secaoSimuladaAtual->idArmazemDono;
            int idNovoDestino = primeiroNoDaNovaRota->proximo->idArmazem;
            SecaoSimulada* novaSecaoSimulada = planejador.BuscaSecao(idNovaOrigem, idNovoDestino);

            if (!novaSecaoSimulada || !novaSecaoSimulada->temEspaco(1)) {
                std::cout <<  std::setw(7) << std::setfill('0') << tempoAtual << " pacote " <<  std::setw(3) << std::setfill('0') << p->getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Congestionamento na proxima secao da rota alternativa (" << idNovaOrigem << " -> " << idNovoDestino << ")." << std::endl;
                idsParaEspera.enfileira(p->getIdUnico());
                continue; 
            }
            // --- SUCESSO NA REROTA: REMANEJAMENTO IMEDIATO ---

            // 3. Atualiza a rota do objeto real.
            ListaEncadeadaRota* novaRotaAlocada = new ListaEncadeadaRota(novaRota);
            p->setRota(novaRotaAlocada); 
            int idArmazemReal;
            PilhaPacotes* pilhaAntiga = EncontraPilhaDoPacote(p->getIdUnico(), idArmazemReal);
            if (pilhaAntiga == nullptr) continue; 
            pilhaAntiga->RemovePacotePorId(p->getIdUnico());
            p->setRota(new ListaEncadeadaRota(novaRota));
            int idSecaoNova = p->getProximoArmazemNaRota();
            PilhaPacotes* pilhaNova = topologiaArmazens->GetArmazem(idArmazemReal)->GetSecao(idSecaoNova);
            
            if (pilhaNova) {
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << p->getIdUnico() 
                          << " REMANEJADO: Movido da secao " << pilhaAntiga->GetIDEnvio() 
                          << " para a secao " << idSecaoNova << " no armazem " << idArmazemReal << "." << std::endl;
                
                pilhaNova->empilhaPacote(p);
            }
            // --- FIM DO REMANEJAMENTO ---
        }
        secaoSimuladaAtual = secaoSimuladaAtual->proximo;
    }


     // --- PASSO E: EXECUTAR O PLANO (AGRUPAR PACOTES E AGENDAR EVENTOS) ---

    // E.1: Agrupamos os pacotes aprovados por sua seção de partida.
    struct GrupoDespacho {
        Armazem* armazemOrigem;
        int idSecao;
        Fila<Pacote*> pacotes; 
        GrupoDespacho* proximo = nullptr;
    };
    GrupoDespacho* primeiroGrupo = nullptr;

    // Itera na topologia REAL, que já está com os pacotes remanejados.
    TopologiaArmazensVerticeNo* noExecucao = topologiaArmazens->primeiroVertice;
    while(noExecucao != nullptr) {
        SecoesArmazem* secoesReais = noExecucao->armazem->GetSecoes();
        if(secoesReais) {
            TipoCelula* celulaReal = secoesReais->GetPrimeiroCelula();
            while(celulaReal != nullptr) {
                PilhaPacotes* pilhaDaSecao = celulaReal->pilhaSecao;
                Fila<Pacote*> pacotesAprovadosNestaSecao;

                if (pilhaDaSecao && !pilhaDaSecao->estaVazia()) {
                    PilhaPacotesNode* atualNode = pilhaDaSecao->getPrimeiroNode(); 
                    Pacote* p = pilhaDaSecao->getPrimeiro(); 

                    while(p != nullptr) {
                        if(!idsParaEspera.contem(p->getIdUnico())) {
                            pacotesAprovadosNestaSecao.enfileira(p);
                        }
                        p = pilhaDaSecao->ObterProximoPacote(p);  
                    }
                }

                // Se encontramos pacotes aprovados para esta seção, criamos um grupo de despacho.
                if (!pacotesAprovadosNestaSecao.estaVazia()) {
                    GrupoDespacho* novoGrupo = new GrupoDespacho();
                    novoGrupo->armazemOrigem = noExecucao->armazem;
                    novoGrupo->idSecao = celulaReal->pilhaSecao->GetIDEnvio();
                    novoGrupo->pacotes = pacotesAprovadosNestaSecao;

                    novoGrupo->proximo = primeiroGrupo;
                    primeiroGrupo = novoGrupo;
                }
                celulaReal = celulaReal->proximo;
            }
        }
        noExecucao = noExecucao->proximo;
    }

    // E.2: Agendamos um evento de transporte real para cada grupo de despacho.
    GrupoDespacho* grupoAtual = primeiroGrupo;
    while(grupoAtual != nullptr) {
        escalonador->AgendarEvento(
            new Evento(tempoAtual, 
                       EVENTO_INICIA_TRANSPORTE, 
                       grupoAtual->armazemOrigem, 
                       grupoAtual->idSecao, 
                       grupoAtual->pacotes)
        );
        
        GrupoDespacho* proximoGrupo = grupoAtual->proximo;
        delete grupoAtual;
        grupoAtual = proximoGrupo;
    }

    // --- PASSO F: REAGENDAR O PRÓXIMO CICLO DE PLANEJAMENTO ---
    double tempoProximoCiclo = tempoAtual + GetIntervaloTransporte();
    escalonador->AgendarEvento(new Evento(tempoProximoCiclo, EVENTO_PREVISAO_TRANSPORTE, nullptr, -1));
}