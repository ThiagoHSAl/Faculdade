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


void Transporte::CoordenarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, Fila<Pacote>& pacotesAprovados, double tempoAtual, Escalonador* escalonador) {
    PilhaPacotes* pilhaReal = armazemOrigem->GetSecao(idSecao);
    if (!pilhaReal || pacotesAprovados.estaVazia()) {
        return;
    }

    // Estrutura auxiliar para buscar IDs aprovados
    Fila<int> idsAprovados;
    while(!pacotesAprovados.estaVazia()){
        idsAprovados.enfileira(pacotesAprovados.desenfileira().getIdUnico());
    }

    // Pilhas temporárias para separar os pacotes da seção real
    PilhaPacotes tempParaManter;
    PilhaPacotes tempParaTransportar;

    // Esvazia a pilha real, separando os pacotes
    while (!pilhaReal->estaVazia()) {
        Pacote p = pilhaReal->desempilhaPacote();
        // TODO: A função 'contem' precisa ser implementada em Fila<int>
        if (idsAprovados.contem(p.getIdUnico())) {
            tempParaTransportar.empilhaPacote(p);
        } else {
            tempParaManter.empilhaPacote(p);
        }
    }

    // Re-empilha os pacotes que devem esperar no armazém
    while (!tempParaManter.estaVazia()) {
        pilhaReal->empilhaPacote(tempParaManter.desempilhaPacote());
    }

    // Agora, tempParaTransportar contém apenas os pacotes aprovados, na ordem correta de remoção (LIFO)
    
    // Delega as próximas tarefas para as funções especialistas
    PilhaPacotes pacotesProntosParaTransporte;
    PilhaPacotes pacotesSobraram;
    double tempoFimRemocao = tempoAtual;

    // Chama o "empacotador"
    ProcessarRemocao(&tempParaTransportar, pacotesProntosParaTransporte, tempoAtual, armazemOrigem->GetIdArmazem(), idSecao, tempoFimRemocao);
    
    // Chama o "carregador"
    Armazem* armazemDestino = topologiaArmazens->GetArmazem(idSecao);
    ProcessarTransporte(pacotesProntosParaTransporte, pacotesSobraram, tempoFimRemocao, armazemOrigem, armazemDestino, escalonador);

    // Chama o "repositor" para os pacotes que não couberam no transporte
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
        Pacote pacote = pilhaInvertida.desempilhaPacote();
        tempoFimRemocao += custoRemocao;

        double duracaoEstadia = tempoFimRemocao - pacote.getTempoEntradaArmazemAtual();
        pacote.setTempoArmazenado(pacote.getTempoArmazenado() + duracaoEstadia);

        std::string qualArmazemQualSecao = armazemESecaoFormatado(idArmazem, idSecao);
        imprimirLinhaFormatada(tempoFimRemocao, pacote.getIdUnico(), "removido de", qualArmazemQualSecao);
        pacote.setEstadoAtual(REMOVIDO);

        pacotesProntos.empilhaPacote(pacote);
    }
}


void Transporte::ProcessarTransporte(PilhaPacotes& pacotesProntos, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, Armazem* armazemOrigem, Armazem* armazemDestino, Escalonador* escalonador) {
    int pacotesEnviados = 0;
    // A capacidade de transporte agora é lida da topologia para a rota específica
    int capacidadeDaRota = topologiaArmazens->GetCapacidadeAresta(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());

    while (!pacotesProntos.estaVazia()) {
        Pacote pacote = pacotesProntos.desempilhaPacote();

        if (pacotesEnviados < capacidadeDaRota) {
           int idPacote = pacote.getIdUnico();
            std::string deOndeparaOnde = origemEDestinoFormatado(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());
            imprimirLinhaFormatada(tempoFimRemocao, idPacote, "em transito", deOndeparaOnde);
            
            pacote.setEstadoAtual(CHEGADA_ESCALONADA);
            pacote.setTempoInicioTransito(tempoFimRemocao);
            double latenciaDaRota = topologiaArmazens->GetLatenciaAresta(armazemOrigem->GetIdArmazem(), armazemDestino->GetIdArmazem());
            double tempoChegada = tempoFimRemocao + latenciaDaRota;
            
            escalonador->AgendarEvento(new Evento(tempoChegada, EVENTO_ARMAZENAMENTO, new Pacote(pacote), armazemDestino));
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
        Pacote pacote = pilhaRearmazenamento.desempilhaPacote();

        pacote.setTempoEntradaArmazemAtual(tempoFimRemocao);
        pacote.setEstadoAtual(ARMAZENADO);

        pilhaSecao->empilhaPacote(pacote);

        std::string qualArmazemQualSecao = armazemESecaoFormatado(IdArmazem, idSecao);
        int idPacote = pacote.getIdUnico();
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
        armazemChegada->ArmazenaPacote(*pacote, idSecao);
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
    destinoFinal->empilhaPacote(*pacote);
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

    armazemInicial->ArmazenaPacote(*pacote, idProximoArmazem);

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

PilhaPacotes* Transporte::EncontraPilhaDoPacote(int id, Pacote& outPacote) {
    TopologiaArmazensVerticeNo* noBusca = topologiaArmazens->primeiroVertice;
    while(noBusca != nullptr) {
        SecoesArmazem* secoes = noBusca->armazem->GetSecoes();
        if (secoes) {
            TipoCelula* celula = secoes->GetPrimeiroCelula();
            while(celula != nullptr) {
                PilhaPacotes* secaoReal = celula->pilhaSecao;
                if(secaoReal && !secaoReal->estaVazia()) {
                    // Para encontrar o pacote, precisamos de uma função na Pilha,
                    // ou iteramos em uma cópia.
                    PilhaPacotes copia = *secaoReal;
                    while(!copia.estaVazia()) {
                        Pacote p = copia.desempilhaPacote();
                        if (p.getIdUnico() == id) {
                            outPacote = p;
                            return secaoReal; // Retorna ponteiro para a pilha real
                        }
                    }
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
    int CAPACIDADE_SECAO = 2; // TODO: Obter este valor do arquivo de input.
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
                    // Percorre a pilha real para obter ponteiros para os pacotes originais
                    Pacote* pacoteAtualNaPilha = secaoReal->getPrimeiro(); // Necessário criar getPrimeiro()
                    int custoRemocaoAcumulado = 1;
                    while(pacoteAtualNaPilha != nullptr){
                        double latencia = topologiaArmazens->GetLatenciaAresta(noBusca->armazem->GetIdArmazem(), secaoReal->GetIDEnvio());
                        double tempoChegada = tempoAtual + (custoRemocaoAcumulado++) + latencia;
                        
                        // Passamos o PONTEIRO para o pacote, não uma cópia
                        pacotesOrdenadosPorChegada.Insere(new PacoteComPrevisao(pacoteAtualNaPilha, tempoChegada, noBusca->armazem->GetIdArmazem()));
                        pacoteAtualNaPilha = pacoteAtualNaPilha->getProximo();
                    }
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
        int idDestino = previsao->pacote.getProximoArmazemNaRota();

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

   // --- PASSO C: SIMULAR CHEGADAS E IDENTIFICAR CONGESTIONAMENTOS ---
    while(!pacotesOrdenadosPorChegada.EstaVazia()) {
        PacoteComPrevisao* chegada = pacotesOrdenadosPorChegada.ExtraiMin();
        
        int armazemChegadaId = -1;
        if(chegada->pacote.getRota() && chegada->pacote.getRota()->GetAtualNaRota()){
             armazemChegadaId = chegada->pacote.getProximoArmazemNaRota();
        }

        if (armazemChegadaId == -1) {
             delete chegada;
             continue;
        }

        int proximoDestinoId = -1;
        if(chegada->pacote.getRota()->GetAtualNaRota()->proximo && chegada->pacote.getRota()->GetAtualNaRota()->proximo->proximo){
            proximoDestinoId = chegada->pacote.getRota()->GetAtualNaRota()->proximo->proximo->idArmazem;
        }
    
        SecaoSimulada* secaoSimulada = planejador.BuscaSecao(armazemChegadaId, proximoDestinoId);

        if (secaoSimulada) {
            // LÓGICA CORRIGIDA: Calcula o espaço disponível real
            int numSaindo = 0;
            ManifestoPartida* manifestoBusca = primeiroManifesto;
            while(manifestoBusca != nullptr){
                if(manifestoBusca->idArmazem == armazemChegadaId && manifestoBusca->idSecao == proximoDestinoId){
                    numSaindo = manifestoBusca->contagemSaidas;
                    break;
                }
                manifestoBusca = manifestoBusca->proximo;
            }

            // Ocupação líquida = (pacotes já na seção - os que vão sair) + os que já chegaram na simulação
            int ocupacaoLiquidaAtual = (secaoSimulada->pacotesAtuais.getTamanho() - numSaindo) + secaoSimulada->pacotesPrevistos.getTamanho();
            
            if (ocupacaoLiquidaAtual < secaoSimulada->capacidade) {
                secaoSimulada->pacotesPrevistos.empilhaPacote(chegada->pacote);
            } else {
                std::cout << tempoAtual << " pacote " << chegada->pacote.getIdUnico() << " Detectado gargalo real, buscando alternativas" << std::endl;
                secaoSimulada->pacotesEmEspera.enfileira(chegada->pacote);
            }
        }
        delete chegada;
    }

     // Limpeza da memória do manifesto
    // ...

    // --- PASSO D: ANALISAR PACOTES EM ESPERA E REMANEJAR IMEDIATAMENTE ---
    
    // Fila que guardará apenas os IDs dos pacotes que devem esperar.
    Fila<int> idsParaEspera;

    SecaoSimulada* secaoSimuladaAtual = planejador.GetPrimeira();
    while (secaoSimuladaAtual != nullptr) {
        // Usamos uma cópia da fila de espera para poder modificá-la durante a iteração
        Fila<Pacote> copiaEspera = secaoSimuladaAtual->pacotesEmEspera;
        while (!copiaEspera.estaVazia()) {
            Pacote p = copiaEspera.desenfileira();
            
            ListaEncadeadaRota novaRota = CalculaRotaDijkstra(secaoSimuladaAtual->idArmazemDono, p.getArmazemDestino(), secaoSimuladaAtual->idSecaoDestino);

            // --- Início do Bloco de Decisão Refatorado ---
            // 1. Cláusula de Guarda: Verifica se não há uma rota alternativa viável.
            // Uma rota viável precisa de pelo menos um trecho, ou seja, 2 nós.
            if (novaRota.GetTamanho() <= 1) {
                idsParaEspera.enfileira(p.getIdUnico());
                std::cout << tempoAtual << " pacote " << p.getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Nenhuma rota alternativa viavel encontrada." << std::endl;
                continue; // Passa para o próximo pacote em espera.
            }

            // Se chegou aqui, a rota existe. Vamos calcular e comparar as latências.
            double latenciaNova = novaRota.CalculaLatenciaTotal(topologiaArmazens);
            double latenciaAntigaRestante = p.getRota()->CalculaLatenciaRestante(topologiaArmazens);

            // 2. Cláusula de Guarda: Verifica se a nova rota é muito mais lenta.
            if (latenciaNova > latenciaAntigaRestante + GetIntervaloTransporte()) {
                std::cout << tempoAtual << " pacote " << p.getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Rota alternativa e muito longa (Latencia: " << latenciaNova << ")." << std::endl;
                idsParaEspera.enfileira(p.getIdUnico());
                continue; // Passa para o próximo pacote em espera.
            }

            // Se chegou aqui, a latência é aceitável. Vamos verificar a capacidade do novo destino.
            RotaNo* primeiroNoDaNovaRota = novaRota.GetPrimeiroNo();

            // 3. Cláusula de Guarda: Verifica se a nova seção de destino é válida e se tem espaço.
            // Adicionamos uma verificação de segurança extra para o ponteiro 'proximo'.
            if (primeiroNoDaNovaRota == nullptr || primeiroNoDaNovaRota->proximo == nullptr) {
                idsParaEspera.enfileira(p.getIdUnico());
                continue;
            }
            int idNovaOrigem = secaoSimuladaAtual->idArmazemDono;
            int idNovoDestino = primeiroNoDaNovaRota->proximo->idArmazem;
            SecaoSimulada* novaSecaoSimulada = planejador.BuscaSecao(idNovaOrigem, idNovoDestino);

            if (!novaSecaoSimulada || !novaSecaoSimulada->temEspaco(1)) {
                std::cout << tempoAtual << " pacote " << p.getIdUnico() << " AGUARDANDO PROXIMO CICLO DE TRANSPORTE: Congestionamento na proxima secao da rota alternativa (" << idNovaOrigem << " -> " << idNovoDestino << ")." << std::endl;
                idsParaEspera.enfileira(p.getIdUnico());
                continue; // Passa para o próximo pacote em espera.
            }


            // --- SUCESSO NA REROTA: REMANEJAMENTO IMEDIATO ---
            
            // 1. Encontra a localização do pacote REAL na topologia.
            int idArmazemReal, idSecaoAntiga;
            Pacote pacoteOriginal;
            PilhaPacotes* pilhaAntiga = EncontraPilhaDoPacote(p.getIdUnico(), pacoteOriginal);

            if (pilhaAntiga == nullptr) continue; // Segurança

            // 2. Remove o pacote da sua seção antiga.
            Pacote pacoteRemovido = pilhaAntiga->RemovePacotePorId(p.getIdUnico());

            // 3. Atualiza a rota do objeto real que acabamos de remover.
            pacoteRemovido.setRota(new ListaEncadeadaRota(novaRota));

            // 4. Adiciona o pacote atualizado na sua NOVA seção de partida.
            int idArmazemDePartida = secaoSimuladaAtual->idArmazemDono;
            int idSecaoNova = pacoteRemovido.getProximoArmazemNaRota();
            PilhaPacotes* pilhaNova = topologiaArmazens->GetArmazem(idArmazemDePartida)->GetSecao(idSecaoNova);
            
            if (pilhaNova) {
                std::cout << tempoAtual << " pacote " << pacoteRemovido.getIdUnico() << " REMANEJADO: Movido da secao " << idSecaoAntiga << " para a secao " << idSecaoNova << std::endl;
                pilhaNova->empilhaPacote(pacoteRemovido);
            }
        }
        secaoSimuladaAtual = secaoSimuladaAtual->proximo;
    }


    // --- PASSO E: EXECUTAR O PLANO (AGRUPAR PACOTES E AGENDAR EVENTOS) ---

    // E.1: Agrupamos os pacotes aprovados por sua seção de partida.
    // Para isso, criamos uma lista encadeada temporária de "Grupos de Despacho".
    struct GrupoDespacho {
        Armazem* armazemOrigem;
        int idSecao;
        Fila<Pacote> pacotes;
        GrupoDespacho* proximo = nullptr;
    };
    GrupoDespacho* primeiroGrupo = nullptr;

    // Itera na topologia REAL, que já está com os pacotes remanejados em suas seções corretas.
    TopologiaArmazensVerticeNo* noExecucao = topologiaArmazens->primeiroVertice;
    while(noExecucao != nullptr) {
        SecoesArmazem* secoesReais = noExecucao->armazem->GetSecoes();
        if(secoesReais) {
            TipoCelula* celulaReal = secoesReais->GetPrimeiroCelula();
            while(celulaReal != nullptr) {
                PilhaPacotes* pilhaDaSecao = celulaReal->pilhaSecao;
                Fila<Pacote> pacotesAprovadosNestaSecao;

                if (pilhaDaSecao && !pilhaDaSecao->estaVazia()) {
                    // Usamos uma cópia da pilha para não destruir a original durante a verificação.
                    PilhaPacotes tempCopia = *pilhaDaSecao;
                    while(!tempCopia.estaVazia()){
                        Pacote p = tempCopia.desempilhaPacote();
                        
                        // LÓGICA FINAL: Um pacote é aprovado se ele NÃO estiver na lista de espera.
                        if(!idsParaEspera.contem(p.getIdUnico())) {
                            pacotesAprovadosNestaSecao.enfileira(p);
                        }
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