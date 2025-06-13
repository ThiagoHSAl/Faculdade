#include "Transporte.hpp"
#include "Escalonador.hpp"
#include "FilaIDs.hpp"
#include "NoInfoBFS.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <vector>


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
Transporte::Transporte(TopologiaArmazens* t, double latencia, int capacidade, double custo, double intervalo) {
    topologiaArmazens = t;
    latenciaTransporte = latencia;
    capacidadeTransporte = capacidade;
    custoRemocao = custo;
    intervaloTransporte = intervalo;
}


Transporte::~Transporte() {}


double Transporte::GetIntervaloTransporte() const {
    return intervaloTransporte;
}


void Transporte::CoordenarCicloDeTransporte(Armazem* armazemOrigem, int idSecao, double tempoAtual, Escalonador* escalonador) {
    if (!armazemOrigem || !escalonador){
        return;
    }

    PilhaPacotes* pilhaSecao = armazemOrigem->GetSecao(idSecao);
    if (!pilhaSecao || pilhaSecao->estaVazia()){
        return;
    } 

    int idDestinoVizinho = pilhaSecao->GetIDEnvio();
    Armazem* armazemDestinoVizinho = topologiaArmazens->GetArmazem(idDestinoVizinho);
    if (!armazemDestinoVizinho){
        return;
    } 
    
    PilhaPacotes pacotesRemovidos;
    PilhaPacotes pacotesParaRearmazenar;
    double tempoFimRemocao = tempoAtual;
    ProcessarRemocao(pilhaSecao, pacotesRemovidos, tempoAtual, armazemOrigem->GetIdArmazem(), idSecao, tempoFimRemocao);
    ProcessarTransporte(pacotesRemovidos, pacotesParaRearmazenar, tempoFimRemocao, armazemOrigem, armazemDestinoVizinho, escalonador);
    ProcessarRearmazenamento(pilhaSecao, pacotesParaRearmazenar, tempoFimRemocao, armazemOrigem->GetIdArmazem(), idSecao);
}


void Transporte::ProcessarRemocao(PilhaPacotes* pilhaSecao, PilhaPacotes& pacotesProntosParaTransporte, double tempoAtual, int IdArmazem, int idSecao, double& tempoFimRemocao) {
    double tempoEventoRemocao = tempoAtual;

    while (!pilhaSecao->estaVazia()) {
        Pacote pacote = pilhaSecao->desempilhaPacote();
        tempoEventoRemocao += custoRemocao;

        double duracaoEstadia = tempoEventoRemocao - pacote.getTempoEntradaArmazemAtual();
        pacote.setTempoArmazenado(pacote.getTempoArmazenado() + duracaoEstadia);

        int idPacote = pacote.getIdUnico();
        std::string qualArmazemQualSecao = armazemESecaoFormatado(IdArmazem, idSecao);
        imprimirLinhaFormatada(tempoEventoRemocao, idPacote, "removido de", qualArmazemQualSecao);
        pacote.setEstadoAtual(REMOVIDO);

        pacotesProntosParaTransporte.empilhaPacote(pacote);
    }
    tempoFimRemocao = tempoEventoRemocao;
}


void Transporte::ProcessarTransporte(PilhaPacotes& pacotesProntosParaTransporte, PilhaPacotes& pacotesSobraram, double tempoFimRemocao, Armazem* armazemOrigem, Armazem* armazemDestino, Escalonador* escalonador) {
    int pacotesEnviados = 0;

    while (!pacotesProntosParaTransporte.estaVazia()) {
        Pacote pacote = pacotesProntosParaTransporte.desempilhaPacote();

        if (pacotesEnviados < capacidadeTransporte) {
            int idPacote = pacote.getIdUnico();
            int idArmazemOrigem = armazemOrigem->GetIdArmazem();
            int idArmazemDestino = armazemDestino->GetIdArmazem();
            std::string deOndeparaOnde = origemEDestinoFormatado(idArmazemOrigem, idArmazemDestino);
            imprimirLinhaFormatada(tempoFimRemocao, idPacote, "em transito", deOndeparaOnde);
            pacote.setEstadoAtual(CHEGADA_ESCALONADA);

            pacote.setTempoInicioTransito(tempoFimRemocao);
            double tempoChegada = tempoFimRemocao + latenciaTransporte;
            escalonador->AgendarEvento(new Evento(tempoChegada, EVENTO_ARMAZENAMENTO, new Pacote(pacote), armazemDestino));
            pacotesEnviados++;
        } 
        else {
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
ListaEncadeadaRota Transporte::CalculaRotaBFS(int idOrigem, int idDestino) {
    if (topologiaArmazens == nullptr) { return ListaEncadeadaRota(); }
    ListaInfoBFS infoNoBFS;
    bool destinoEncontrado = false;
    FilaIDs fila;
    TopologiaArmazensVerticeNo* noAtualGrafo = topologiaArmazens->primeiroVertice;
    while (noAtualGrafo != nullptr) {
        infoNoBFS.AdicionaInfo(noAtualGrafo->armazem->GetIdArmazem());
        noAtualGrafo = noAtualGrafo->proximo;
    }
    infoNoBFS.Reset();
    NoInfoBFS* infoOrigem = infoNoBFS.BuscaInfo(idOrigem);
    NoInfoBFS* infoDestino = infoNoBFS.BuscaInfo(idDestino);
    if (infoOrigem == nullptr || infoDestino == nullptr) { return ListaEncadeadaRota(); }
    infoOrigem->distancia = 0;
    infoOrigem->visitado = true;
    fila.enfileira(idOrigem);
    while (!fila.estaVazia()) {
        int idU = fila.desenfileira();
        NoInfoBFS* infoU = infoNoBFS.BuscaInfo(idU);
        if (idU == idDestino) {
            destinoEncontrado = true;
            break;
        }
        SecoesArmazem* secoesU = topologiaArmazens->GetSecoesArmazem(idU);
        if (secoesU != nullptr) {
            TipoCelula* celulaSecaoAtual = secoesU->GetPrimeiroCelula();
            while(celulaSecaoAtual != nullptr) {
                if (celulaSecaoAtual->pilhaSecao != nullptr) {
                    int idVizinhoV = celulaSecaoAtual->pilhaSecao->GetIDEnvio();
                    NoInfoBFS* infoV = infoNoBFS.BuscaInfo(idVizinhoV);
                    if (infoV != nullptr && !infoV->visitado) {
                        infoV->visitado = true;
                        infoV->distancia = infoU->distancia + 1;
                        infoV->idPredecessor = idU;
                        fila.enfileira(idVizinhoV);
                    }
                }
                celulaSecaoAtual = celulaSecaoAtual->proximo;
            }
        }
    }
    if (!destinoEncontrado) { return ListaEncadeadaRota(); }
    ListaEncadeadaRota rotaResultante;
    int idNoAtualRota = idDestino;
    while (idNoAtualRota != -1) {
        rotaResultante.InsereNoInicio(idNoAtualRota);
        NoInfoBFS* infoAtual = infoNoBFS.BuscaInfo(idNoAtualRota);
        if (infoAtual != nullptr) {
            idNoAtualRota = infoAtual->idPredecessor;
        } else {
            idNoAtualRota = -1;
        }
    }
    return rotaResultante;
}

bool Transporte::CalculaEAtribuiRota(Pacote* pacote) {
    if (pacote == nullptr) { return false; }
    ListaEncadeadaRota rota_calculada_obj = CalculaRotaBFS(pacote->getArmazemOrigem(), pacote->getArmazemDestino());
    if (rota_calculada_obj.GetTamanho() > 0) {
        pacote->setRota(new ListaEncadeadaRota(rota_calculada_obj)); 
        return true;
    } else {
        return false;
    }
}