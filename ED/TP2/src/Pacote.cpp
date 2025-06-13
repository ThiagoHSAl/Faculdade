#include "Pacote.hpp"
#include "ListaEncadeadaRota.hpp"
#include <iostream>
#include <string>

Pacote::Pacote() {
    dataPostagem = {0, 0, 0};
    timestampPostagem;
    remetente = "";
    destinatario = "";
    tipo = "";
    armazemOrigem = -1;
    armazemDestino = -1;
    idUnico = -1;
    rota = nullptr;
    estadoAtual = NAO_POSTADO;
    proximo = nullptr;
    tempoEsperadoEstadia = 0.0;
    tempoArmazenado = 0.0;
    tempoEmTransito = 0.0;
    tempoEntradaArmazemAtual = 0.0;
    tempoSaidaArmazemAtual = 0.0;
    tempoInicioTransito = 0.0;
    tempoFimTransito = 0.0;
}

Pacote::Pacote(data dp, std::string rem, std::string dest, int origem, int destino, std::string tp, int id, double ts_postagem) {
    timestampPostagem = ts_postagem;
    dataPostagem = dp;
    remetente = rem;
    destinatario = dest;
    tipo = tp;
    armazemOrigem = origem;
    armazemDestino = destino;
    idUnico = id;
    rota = nullptr;
    estadoAtual = NAO_POSTADO;
    proximo = nullptr;
    tempoEsperadoEstadia = 0.0;
    tempoArmazenado = 0.0;
    tempoEmTransito = 0.0;
    tempoEntradaArmazemAtual = 0.0;
    tempoSaidaArmazemAtual = 0.0;
    tempoInicioTransito = 0.0;
    tempoFimTransito = 0.0;
}

Pacote::Pacote(const Pacote& other) {
    dataPostagem = other.dataPostagem;
    timestampPostagem = other.timestampPostagem;
    remetente = other.remetente;
    destinatario = other.destinatario;
    tipo = other.tipo;
    armazemOrigem = other.armazemOrigem;
    armazemDestino = other.armazemDestino;
    idUnico = other.idUnico;
    estadoAtual = other.estadoAtual;
    tempoEsperadoEstadia = other.tempoEsperadoEstadia;
    tempoArmazenado = other.tempoArmazenado;
    tempoEmTransito = other.tempoEmTransito;
    tempoEntradaArmazemAtual = other.tempoEntradaArmazemAtual;
    tempoSaidaArmazemAtual = other.tempoSaidaArmazemAtual;
    tempoInicioTransito = other.tempoInicioTransito;
    tempoFimTransito = other.tempoFimTransito;

    proximo = nullptr;

    if (other.rota != nullptr) {
        rota = new ListaEncadeadaRota(*other.rota);
    } else {
        rota = nullptr;
    }
}

Pacote& Pacote::operator=(const Pacote& other) {
    if (this == &other) {
        return *this;
    }

    dataPostagem = other.dataPostagem;
    timestampPostagem = other.timestampPostagem;
    remetente = other.remetente;
    destinatario = other.destinatario;
    tipo = other.tipo;
    armazemOrigem = other.armazemOrigem;
    armazemDestino = other.armazemDestino;
    idUnico = other.idUnico;
    estadoAtual = other.estadoAtual;
    tempoEsperadoEstadia = other.tempoEsperadoEstadia;
    tempoArmazenado = other.tempoArmazenado;
    tempoEmTransito = other.tempoEmTransito;
    tempoEntradaArmazemAtual = other.tempoEntradaArmazemAtual;
    tempoSaidaArmazemAtual = other.tempoSaidaArmazemAtual;
    tempoInicioTransito = other.tempoInicioTransito;
    tempoFimTransito = other.tempoFimTransito;

    delete rota;
    if (other.rota != nullptr) {
        rota = new ListaEncadeadaRota(*other.rota);
    } else {
        rota = nullptr;
    }

    return *this;
}

Pacote::~Pacote() {
    delete rota;
}

data Pacote::getDataPostagem() const { return dataPostagem; }
std::string Pacote::getRemetente() const { return remetente; }
std::string Pacote::getDestinatario() const { return destinatario; }
std::string Pacote::getTipo() const { return tipo; }
int Pacote::getArmazemOrigem() const { return armazemOrigem; }
int Pacote::getArmazemDestino() const { return armazemDestino; }
int Pacote::getIdUnico() const { return idUnico; }
ListaEncadeadaRota* Pacote::getRota() const { return rota; }
EstadoPacote Pacote::getEstadoAtual() const { return estadoAtual; }
Pacote* Pacote::getProximo() const { return proximo; }
double Pacote::getTempoEsperadoEstadia() const { return tempoEsperadoEstadia; }
double Pacote::getTempoArmazenado() const { return tempoArmazenado; }
double Pacote::getTempoEmTransito() const { return tempoEmTransito; }
double Pacote::getTempoEntradaArmazemAtual() const { return tempoEntradaArmazemAtual; }
double Pacote::getTempoSaidaArmazemAtual() const { return tempoSaidaArmazemAtual; }
double Pacote::getTempoInicioTransito() const { return tempoInicioTransito; }
double Pacote::getTempoFimTransito() const { return tempoFimTransito; }

int Pacote::getProximoArmazemNaRota() const {
    if (rota != nullptr) {
        return rota->GetProximoArmazem();
    }
    return -1;
}

void Pacote::setDataPostagem(data dp) { dataPostagem = dp; }
void Pacote::setRemetente(std::string rem) { remetente = rem; }
void Pacote::setDestinatario(std::string dest) { destinatario = dest; }
void Pacote::setTipo(std::string tp) { tipo = tp; }
void Pacote::setArmazemOrigem(int origem) { armazemOrigem = origem; }
void Pacote::setArmazemDestino(int destino) { armazemDestino = destino; }
void Pacote::setIdUnico(int id) { idUnico = id; }
void Pacote::setEstadoAtual(EstadoPacote estado) { estadoAtual = estado; }
void Pacote::setProximo(Pacote* p) { proximo = p; }
void Pacote::setTempoEsperadoEstadia(double tempo) { tempoEsperadoEstadia = tempo; }
void Pacote::setTempoArmazenado(double tempo) { tempoArmazenado = tempo; }
void Pacote::setTempoEmTransito(double tempo) { tempoEmTransito = tempo; }
void Pacote::setTempoEntradaArmazemAtual(double tempo) { tempoEntradaArmazemAtual = tempo; }
void Pacote::setTempoSaidaArmazemAtual(double tempo) { tempoSaidaArmazemAtual = tempo; }
void Pacote::setTempoInicioTransito(double tempo) { tempoInicioTransito = tempo; }
void Pacote::setTempoFimTransito(double tempo) { tempoFimTransito = tempo; }

void Pacote::setRota(ListaEncadeadaRota* r) {
    if (rota != r) {
        delete rota;
        rota = r;
    }
}

void Pacote::avancaNaRota() {
    if (rota != nullptr) {
        rota->Avanca();
    }
}

bool Pacote::chegouAoDestinoFinal() const {
    if (rota != nullptr) {
        return rota->EstaNoFinal() && rota->GetProximoArmazem() == -1;
    }
    return false;
}

void Pacote::ImprimeRota() const {
    std::cout << "Rota do Pacote ID " << idUnico << " (Origem: " << armazemOrigem << ", Destino: " << armazemDestino << "): ";
    if (rota != nullptr) {
        rota->Imprime();
    } else {
        std::cout << "Nenhuma rota definida." << std::endl;
    }
}

double Pacote::getTimestampPostagem() const {
    return this->timestampPostagem;
}

// Implementação do setter
void Pacote::setTimestampPostagem(double ts) {
    this->timestampPostagem = ts;
}


PilhaPacotes::PilhaPacotes() {
    primeiro = nullptr;
    ultimo = nullptr;
    tamanho = 0;
    IDEnvio = -1;
}

PilhaPacotes::PilhaPacotes(int idEnvio) {
    primeiro = nullptr;
    ultimo = nullptr;
    tamanho = 0;
    this->IDEnvio = idEnvio;
}

PilhaPacotes::~PilhaPacotes() {
    limpa(); 
}

void PilhaPacotes::empilhaPacote(Pacote pacote) {
    Pacote* novoPacote = new Pacote(pacote); 

    if (estaVazia()) {
        primeiro = novoPacote;
        ultimo = novoPacote;
    } else {
        novoPacote->setProximo(primeiro); 
        primeiro = novoPacote;
    }
    tamanho++;
}

Pacote PilhaPacotes::desempilhaPacote() {
    if (estaVazia()) {
        std::cerr << "Erro: Tentativa de desempilhar de uma pilha vazia com IDEnvio " << IDEnvio << "." << std::endl;
        return Pacote(); 
    }

    Pacote* pacoteDesempilhado = primeiro;
    Pacote pacoteRetorno = *pacoteDesempilhado;

    primeiro = primeiro->getProximo(); 
    if (primeiro == nullptr) { 
        ultimo = nullptr;
    }

    delete pacoteDesempilhado; 
    tamanho--;
    return pacoteRetorno;
}

void PilhaPacotes::limpa() {
    while (!estaVazia()) {
        desempilhaPacote();
    }
}

int PilhaPacotes::getTamanho() {
    return tamanho;
}

bool PilhaPacotes::estaVazia() {
    return tamanho == 0;
}

int PilhaPacotes::GetIDEnvio() const {
    return IDEnvio;
}

void PilhaPacotes::Imprime() {
    if (estaVazia()) {
        std::cout << "Vazia"; 
        return;
    }
    Pacote* atual = primeiro;
    while (atual != nullptr) {
        std::cout << atual->getIdUnico() << " ";
        atual = atual->getProximo();
    }
}