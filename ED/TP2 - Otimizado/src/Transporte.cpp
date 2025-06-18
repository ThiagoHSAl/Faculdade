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
Transporte::Transporte(TopologiaArmazens* t, double custo, double intervalo) {
    topologiaArmazens = t;
    custoRemocao = custo;
    intervaloTransporte = intervalo;
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

    // --- LÓGICA CORRIGIDA ---

    // 1. Cria uma pilha temporária para guardar os pacotes que realmente conseguimos remover.
    PilhaPacotes pacotesParaTransportar;

    // 2. Itera sobre a "ordem de serviço" (pacotes aprovados pelo planejador).
    while (!pacotesAprovados.estaVazia()) {
        Pacote* pacoteAprovado = pacotesAprovados.desenfileira();
        if (pacoteAprovado) {
            // 3. Remove "cirurgicamente" o pacote da pilha real usando seu ID.
            // A função RemovePacotePorId já o desvincula da lista original.
            Pacote* pacoteRemovido = pilhaReal->RemovePacotePorId(pacoteAprovado->getIdUnico());
            
            if (pacoteRemovido) {
                // Adiciona o pacote removido à nossa lista de transporte.
                pacotesParaTransportar.empilhaPacote(pacoteRemovido);
            }
        }
    }

    // Se, ao final, nenhum pacote foi de fato removido, não há mais nada a fazer.
    if (pacotesParaTransportar.estaVazia()) {
        return;
    }

    // 4. Agora, 'pilhaReal' contém apenas os pacotes que devem esperar,
    // e 'pacotesParaTransportar' contém apenas os que devem viajar.
    // O resto do processo continua como antes.
    
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

    // Inverte a pilha para processar na ordem correta de remoção (LIFO)
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
    // A capacidade de transporte agora é lida da topologia para a rota específica
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
    // NOVA VERIFICAÇÃO: Se a origem ou o destino for o nó proibido, não há rota possível.
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

        if (idU == idNoProibido) {
            continue;
        }

        NoInfoDijkstra* infoU = infoNos.BuscaInfo(idU);
        if (infoU == nullptr) {
            continue;
        }
        
        if (idU == idDestino) {
            break;
        }

        SecoesArmazem* secoesU = topologiaArmazens->GetSecoesArmazem(idU);
        if (secoesU != nullptr) {
            TipoCelula* celulaVizinho = secoesU->GetPrimeiroCelula();
            while (celulaVizinho != nullptr) {
                int idVizinhoV = celulaVizinho->pilhaSecao->GetIDEnvio();
                double latenciaAresta = celulaVizinho->infoAresta.latencia;
                NoInfoDijkstra* infoV = infoNos.BuscaInfo(idVizinhoV);

                if (infoV != nullptr && infoU->distancia + latenciaAresta < infoV->distancia) {
                    infoV->distancia = infoU->distancia + latenciaAresta;
                    infoV->idPredecessor = idU;
                    filaPrioridade.Insere(new NoHeapDijkstra(idVizinhoV, infoV->distancia));
                }
                celulaVizinho = celulaVizinho->proximo;
            }
        }
    }

    ListaEncadeadaRota rotaResultante;
    int idNoAtualRota = idDestino;
    while (idNoAtualRota != -1) {
        rotaResultante.InsereNoInicio(idNoAtualRota);
        NoInfoDijkstra* infoAtual = infoNos.BuscaInfo(idNoAtualRota);
        if (infoAtual != nullptr) {
            idNoAtualRota = infoAtual->idPredecessor;
        } else {
            idNoAtualRota = -1;
        }
    }

    if (rotaResultante.GetTamanho() <= 1 && idOrigem != idDestino) {
        return ListaEncadeadaRota(); 
    }

    return rotaResultante;
}

bool Transporte::CalculaEAtribuiRota(Pacote* pacote) {
    if (pacote == nullptr) {
        return false;
    }

    // Chama a versão de Dijkstra que aceita um nó proibido (sem proibi-lo nesta chamada inicial)
    ListaEncadeadaRota rota_calculada = CalculaRotaDijkstra(pacote->getArmazemOrigem(), pacote->getArmazemDestino());

    // Verifica se a rota calculada é válida
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
        if (secoes) {
            TipoCelula* celula = secoes->GetPrimeiroCelula();
            while(celula != nullptr) {
                PilhaPacotes* secaoReal = celula->pilhaSecao;
                // Itera de forma segura, sem destruir a pilha
                Pacote* p_atual = secaoReal->getPrimeiro();
                while(p_atual != nullptr) {
                    if (p_atual->getIdUnico() == id) {
                        outIdArmazem = noBusca->armazem->GetIdArmazem();
                        return secaoReal; // Retorna ponteiro para a pilha real
                    }
                    p_atual = p_atual->getProximo();
                }
                celula = celula->proximo;
            }
        }
        noBusca = noBusca->proximo;
    }
    return nullptr; // Não encontrou
}

void Transporte::PlanejarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, double tempoAtual, Escalonador* escalonador) {
    // Esta verificação garante que a lógica de planejamento global só rode uma vez por ciclo,
    // acionada pelo primeiro evento de previsão que for processado.
    static double ultimoTempoPlanejado = -1.0;
    if (tempoAtual == ultimoTempoPlanejado) {
        return; 
    }
    ultimoTempoPlanejado = tempoAtual;

    // --- PASSO A: INICIALIZAR O AMBIENTE DE SIMULAÇÃO ---
    PlanejadorDeCiclo planejador;
    int CAPACIDADE_SECAO = 1; // TODO: Obter este valor do arquivo de input.
    TopologiaArmazensVerticeNo* noSetup = topologiaArmazens->primeiroVertice;
    while(noSetup != nullptr) {
        SecoesArmazem* secoesReais = noSetup->armazem->GetSecoes();
        if(secoesReais) {
            TipoCelula* celulaReal = secoesReais->GetPrimeiroCelula();
            while(celulaReal != nullptr) {
                if(celulaReal->pilhaSecao) {
                    planejador.AdicionarSecao(noSetup->armazem->GetIdArmazem(), celulaReal->pilhaSecao->GetIDEnvio(), CAPACIDADE_SECAO, *celulaReal->pilhaSecao);
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
                    
                    // --- INÍCIO DA LÓGICA CORRIGIDA E SEGURA ---
                    
                    // 1. Calcula o tempo de partida para o grupo INTEIRO desta seção.
                    double tempoDePartidaDaSecao = tempoAtual + (secaoReal->getTamanho() * this->custoRemocao);
                    double latencia = topologiaArmazens->GetLatenciaAresta(noBusca->armazem->GetIdArmazem(), celula->pilhaSecao->GetIDEnvio());
                    double tempoChegada = tempoDePartidaDaSecao + latencia;

                    // 2. Itera sobre a pilha usando ponteiros, de forma NÃO-DESTRUTIVA.
                    // Isso evita a cópia superficial e a corrupção de memória.
                    Pacote* pacoteAtualNaPilha = secaoReal->getPrimeiro();
                    while(pacoteAtualNaPilha != nullptr){
                         // DEBUG: Ao coletar o pacote 0
                        std::cout << "[DEBUG t=" << tempoAtual << "] PASSO B: Pacote " << pacoteAtualNaPilha->getIdUnico() << " encontrado na secao " 
                                    << noBusca->armazem->GetIdArmazem() << "->" << celula->pilhaSecao->GetIDEnvio() 
                                    << ". Adicionando a lista de prioridades." << std::endl;
                        // Passamos o ponteiro para o pacote original.
                        pacotesOrdenadosPorChegada.Insere(new PacoteComPrevisao(pacoteAtualNaPilha, tempoChegada, noBusca->armazem->GetIdArmazem()));
                        // Avança para o próximo pacote na lista encadeada.
                        pacoteAtualNaPilha = pacoteAtualNaPilha->getProximo();
                    }
                    // --- FIM DA LÓGICA CORRIGIDA ---
                }
                celula = celula->proximo;
            }
        }
        noBusca = noBusca->proximo;
    }


    // --- NOVO PASSO B.2: CRIAR MANIFESTO DE PARTIDAS ---
    // Precisamos de uma estrutura para contar quantos pacotes sairão de cada seção.
    // Como não usamos STL, uma lista encadeada simples serve.
    struct ManifestoPartida {
        int idArmazem;
        int idSecao;
        int contagemSaidas = 0;
        ManifestoPartida* proximo = nullptr;
    };
    ManifestoPartida* primeiroManifesto = nullptr;

    // Usamos uma cópia do heap para não esvaziá-lo antes da hora.
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
    while(!pacotesOrdenadosPorChegada.EstaVazia()) {
        PacoteComPrevisao* chegada = pacotesOrdenadosPorChegada.ExtraiMin();

        // DEBUG: Ao simular a chegada do pacote 
            std::cout << "[DEBUG t=" << tempoAtual << "] PASSO C: Simulando chegada do Pacote " << chegada->pacote->getIdUnico() << " no armazem " 
                      << chegada->pacote->getProximoArmazemNaRota() << "." << std::endl;
        
        if (chegada->pacote == nullptr || chegada->pacote->getRota() == nullptr) {
            delete chegada;
            continue;
        }
        
        int armazemChegadaId = chegada->pacote->getProximoArmazemNaRota();

        // Se o pacote chegou ao seu destino final, ele não ocupará uma nova seção.
        if (armazemChegadaId == -1) {
            delete chegada;
            continue;
        }

        // Determina a seção que o pacote tentará ocupar no armazém de chegada.
        int proximoDestinoId = -1;
        RotaNo* noAtualNaRota = chegada->pacote->getRota()->GetAtualNaRota();
        if(noAtualNaRota && noAtualNaRota->proximo && noAtualNaRota->proximo->proximo){
            proximoDestinoId = noAtualNaRota->proximo->proximo->idArmazem;
        }
        
        SecaoSimulada* secaoSimuladaAlvo = planejador.BuscaSecao(armazemChegadaId, proximoDestinoId);

        if (secaoSimuladaAlvo) {
            // --- LÓGICA CORRETA USANDO O MANIFESTO ---

            // 1. Busca no manifesto o número exato de pacotes que sairão da seção de destino.
            int numSaindo = 0;
            ManifestoPartida* manifestoBusca = primeiroManifesto;
            while(manifestoBusca != nullptr){
                if(manifestoBusca->idArmazem == armazemChegadaId && manifestoBusca->idSecao == proximoDestinoId){
                    numSaindo = manifestoBusca->contagemSaidas;
                    break;
                }
                manifestoBusca = manifestoBusca->proximo;
            }

            // 2. Calcula a ocupação líquida usando a contagem precisa do manifesto.
            int ocupacaoInicial = secaoSimuladaAlvo->pacotesAtuais->getTamanho();
            int chegadasJaSimuladas = secaoSimuladaAlvo->pacotesPrevistos->getTamanho();

            // Ocupação Final = (Estavam lá - Vão Sair) + (Já chegaram na simulação) + 1 (este pacote)
            int ocupacaoFinalPrevista = (ocupacaoInicial - numSaindo) + chegadasJaSimuladas + 1;

            if (ocupacaoFinalPrevista <= secaoSimuladaAlvo->capacidade) {
                // NÃO HÁ GARGALO: O espaço será liberado a tempo.
                secaoSimuladaAlvo->pacotesPrevistos->empilhaPacote(chegada->pacote);
            } else {
                // GARGALO REAL DETECTADO: Mesmo com as saídas, não haverá espaço.
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << chegada->pacote->getIdUnico() 
                          << " Congestionamento previsto no armazem " 
                          << armazemESecaoFormatado(armazemChegadaId, proximoDestinoId) 
                          << " (Ocupacao: " << ocupacaoFinalPrevista 
                          << ", Capacidade: " << secaoSimuladaAlvo->capacidade << ")" << std::endl;
                secaoSimuladaAlvo->pacotesEmEspera.enfileira(chegada->pacote);
            }
        }
        
        delete chegada;
    }

    // Limpeza da memória da lista de manifestos após o uso.
    ManifestoPartida* manifestoAtual = primeiroManifesto;
    while(manifestoAtual != nullptr) {
        ManifestoPartida* proximo = manifestoAtual->proximo;
        delete manifestoAtual;
        manifestoAtual = proximo;
    }

    // --- PASSO D: ANALISAR PACOTES EM ESPERA E REMANEJAR IMEDIATAMENTE ---
    
    // Fila que guardará apenas os IDs dos pacotes que devem esperar.
    Fila<int> idsParaEspera;

    SecaoSimulada* secaoSimuladaAtual = planejador.GetPrimeira();
    while (secaoSimuladaAtual != nullptr) {
        // Usamos uma cópia da fila de espera para poder modificá-la durante a iteração
        Fila<Pacote*> copiaEspera = secaoSimuladaAtual->pacotesEmEspera;
        while (!copiaEspera.estaVazia()) {
            Pacote* p = copiaEspera.desenfileira();
            // DEBUG: Ao analisar o pacote 0 na fila de espera
                std::cout << "[DEBUG t=" << tempoAtual << "] PASSO D: Analisando Pacote "<< p->getIdUnico() <<" que estava em espera." << std::endl;
            ListaEncadeadaRota novaRota = CalculaRotaDijkstra(secaoSimuladaAtual->idArmazemDono, p->getArmazemDestino(), secaoSimuladaAtual->idSecaoDestino);

            // --- Início do Bloco de Decisão Refatorado ---
            // 1. Cláusula de Guarda: Verifica se não há uma rota alternativa viável.
            // Uma rota viável precisa de pelo menos um trecho, ou seja, 2 nós.
            if (novaRota.GetTamanho() <= 1) {
                idsParaEspera.enfileira(p->getIdUnico());
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << p->getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Nenhuma rota alternativa viavel encontrada." << std::endl;
                continue; // Passa para o próximo pacote em espera.
            }

            // Se chegou aqui, a rota existe. Vamos calcular e comparar as latências.
            double latenciaNova = novaRota.CalculaLatenciaTotal(topologiaArmazens);
            double latenciaAntigaRestante = p->getRota()->CalculaLatenciaRestante(topologiaArmazens);

            // 2. Cláusula de Guarda: Verifica se a nova rota é muito mais lenta.
            if (latenciaNova > latenciaAntigaRestante + GetIntervaloTransporte()) {
                std::cout << std::setw(7) << std::setfill('0') << tempoAtual << " pacote " <<  std::setw(3) << std::setfill('0') << p->getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Rota alternativa e muito longa (Latencia: " << latenciaNova << ")." << std::endl;
                idsParaEspera.enfileira(p->getIdUnico());
                continue; // Passa para o próximo pacote em espera.
            }

            // Se chegou aqui, a latência é aceitável. Vamos verificar a capacidade do novo destino.
            RotaNo* primeiroNoDaNovaRota = novaRota.GetPrimeiroNo();

            // 3. Cláusula de Guarda: Verifica se a nova seção de destino é válida e se tem espaço.
            // Adicionamos uma verificação de segurança extra para o ponteiro 'proximo'.
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
                continue; // Passa para o próximo pacote em espera.
            }


            // --- SUCESSO NA REROTA: REMANEJAMENTO IMEDIATO ---
            
            // --- SUCESSO NA REROTA: REMANEJAMENTO IMEDIATO E SEGURO ---
            
            // 1. Encontra a pilha ONDE o pacote real está.
            int idArmazemReal;
            PilhaPacotes* pilhaAntiga = EncontraPilhaDoPacote(p->getIdUnico(), idArmazemReal);

            if (pilhaAntiga == nullptr) continue; // Segurança: se não achar, não faz nada.

            // 2. Remove o pacote da sua seção antiga. 'p' é o ponteiro para o pacote real.
            pilhaAntiga->RemovePacotePorId(p->getIdUnico());

            // 3. Atualiza a rota do objeto real.
            p->setRota(new ListaEncadeadaRota(novaRota));

            // 4. Adiciona o pacote (já com a rota atualizada) na sua NOVA seção de partida.
            int idSecaoNova = p->getProximoArmazemNaRota();
            PilhaPacotes* pilhaNova = topologiaArmazens->GetArmazem(idArmazemReal)->GetSecao(idSecaoNova);
            
            if (pilhaNova) {
                std::cout << tempoAtual << " pacote " << std::setw(3) << std::setfill('0') << p->getIdUnico() 
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
        Fila<Pacote*> pacotes; // MUDANÇA: A fila agora armazena ponteiros
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
                // MUDANÇA: A fila local também armazena ponteiros
                Fila<Pacote*> pacotesAprovadosNestaSecao;

                if (pilhaDaSecao && !pilhaDaSecao->estaVazia()) {
                    // --- LÓGICA DE ITERAÇÃO CORRIGIDA E NÃO-DESTRUTIVA ---
                    Pacote* p = pilhaDaSecao->getPrimeiro();
                    while(p != nullptr) {
                        // Um pacote é aprovado se ele NÃO estiver na lista de espera.
                        if(!idsParaEspera.contem(p->getIdUnico())) {
                            // MUDANÇA: Enfileiramos o ponteiro, não uma cópia do objeto.
                            // DEBUG: Ao confirmar que o pacote 0 foi aprovado para transporte
                                std::cout << "[DEBUG t=" << tempoAtual << "] PASSO E: Pacote " << p->getIdUnico() << " APROVADO para transporte neste ciclo." << std::endl;
        
                            pacotesAprovadosNestaSecao.enfileira(p);
                        }
                        p = p->getProximo();
                    }
                }
                
                // Se encontramos pacotes aprovados para esta seção, criamos um grupo de despacho.
                if (!pacotesAprovadosNestaSecao.estaVazia()) {
                    GrupoDespacho* novoGrupo = new GrupoDespacho();
                    novoGrupo->armazemOrigem = noExecucao->armazem;
                    novoGrupo->idSecao = celulaReal->pilhaSecao->GetIDEnvio();
                    novoGrupo->pacotes = pacotesAprovadosNestaSecao;
                    
                    // Adiciona o novo grupo no início da lista de grupos.
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
            new Evento(tempoAtual, // O transporte é agendado para começar imediatamente.
                       EVENTO_INICIA_TRANSPORTE, 
                       grupoAtual->armazemOrigem, 
                       grupoAtual->idSecao, 
                       grupoAtual->pacotes)
        );
        
        // Libera a memória da estrutura temporária do grupo de forma segura.
        GrupoDespacho* proximoGrupo = grupoAtual->proximo;
        delete grupoAtual;
        grupoAtual = proximoGrupo;
    }

    // --- PASSO F: REAGENDAR O PRÓXIMO CICLO DE PLANEJAMENTO ---
    double tempoProximoCiclo = tempoAtual + GetIntervaloTransporte();
    escalonador->AgendarEvento(new Evento(tempoProximoCiclo, EVENTO_PREVISAO_TRANSPORTE, nullptr, -1));
}