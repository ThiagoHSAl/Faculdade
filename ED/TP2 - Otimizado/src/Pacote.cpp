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
    tamanho = 0;
    IDEnvio = -1;
}

PilhaPacotes::PilhaPacotes(int idEnvio) : primeiro(nullptr), tamanho(0), IDEnvio(idEnvio) {}

PilhaPacotes::~PilhaPacotes() {
    limpa(); // Call limpa to clean up nodes
}

void PilhaPacotes::empilhaPacote(Pacote* pacote) {
    if (pacote == nullptr) return;
    PilhaPacotesNode* novoNo = new PilhaPacotesNode(pacote); // Create a new internal node
    novoNo->proximo = this->primeiro;
    this->primeiro = novoNo;
    this->tamanho++;
}

Pacote* PilhaPacotes::desempilhaPacote() {
    if (estaVazia()) return nullptr;
    
    PilhaPacotesNode* noRetorno = this->primeiro;
    Pacote* pacoteRetorno = noRetorno->pacote;
    this->primeiro = this->primeiro->proximo;
    this->tamanho--;
    
    noRetorno->proximo = nullptr; // Disconnect the node
    delete noRetorno; // Delete the node, not the package
    return pacoteRetorno;
}

void PilhaPacotes::limpa() {
    PilhaPacotesNode* atual = primeiro;
    while (atual != nullptr) {
        PilhaPacotesNode* proximoTemp = atual->proximo;
        delete atual; // Delete the node, not the package it points to
        atual = proximoTemp;
    }
    primeiro = nullptr;
    tamanho = 0;
}

int PilhaPacotes::getTamanho() const {
    return tamanho;
}

bool PilhaPacotes::estaVazia() const {
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
    // Now 'primeiro' points to a PilhaPacotesNode, not directly to a Pacote*
    PilhaPacotesNode* atualNode = primeiro; 
    while (atualNode != nullptr) {
        // Access the Pacote* from the node
        std::cout << atualNode->pacote->getIdUnico() << " "; 
        // Move to the next PilhaPacotesNode
        atualNode = atualNode->proximo; 
    }
    std::cout << std::endl; // Added for cleaner output after printing all IDs
}

// Implementação do construtor
PacoteComPrevisao::PacoteComPrevisao(Pacote* p, double tempo, int origem)
    : pacote(p), tempoChegada(tempo), armazemOrigemTransporte(origem) {}

// Implementação do operador de comparação
bool PacoteComPrevisao::operator>(const PacoteComPrevisao& other) const {
    // A prioridade é do menor tempo de chegada
    if (this->tempoChegada != other.tempoChegada) {
        return this->tempoChegada > other.tempoChegada;
    }
    // Em caso de empate no tempo de chegada, desempata pelo menor ID do pacote.
    // Isso garante uma ordem determinística para pacotes que chegam no mesmo instante.
    return this->pacote->getIdUnico() > other.pacote->getIdUnico();
}

PilhaPacotes::PilhaPacotes(const PilhaPacotes& other) :
    primeiro(nullptr), tamanho(0), IDEnvio(other.IDEnvio) {
    
    if (other.primeiro == nullptr) {
        return; // Nothing to copy
    }

    // Use a temporary stack to reverse order for correct empilha
    PilhaPacotes temp;
    PilhaPacotesNode* currentOther = other.primeiro;
    while (currentOther != nullptr) {
        temp.empilhaPacote(currentOther->pacote); // Empilha Pacote*
        currentOther = currentOther->proximo;
    }

    // Transfer from temporary stack to this stack (maintains original order)
    PilhaPacotesNode* tempCurrent = temp.primeiro;
    PilhaPacotesNode* prev = nullptr;
    while (tempCurrent != nullptr) {
        PilhaPacotesNode* newNode = new PilhaPacotesNode(tempCurrent->pacote);
        if (primeiro == nullptr) {
            primeiro = newNode;
            prev = newNode;
        } else {
            prev->proximo = newNode;
            prev = newNode;
        }
        tamanho++;
        tempCurrent = tempCurrent->proximo;
    }
    // Crucial: temp's destructor will delete its internal nodes, but not the actual Pacote objects.
    // The temp.primeiro will be set to nullptr by temp's destructor, avoiding double deletion of nodes.
}


// Corrected Deep Copy Assignment Operator for PilhaPacotes
PilhaPacotes& PilhaPacotes::operator=(const PilhaPacotes& other) {
    if (this == &other) {
        return *this;
    }

    limpa(); // Clear existing nodes in 'this'

    IDEnvio = other.IDEnvio;

    if (other.primeiro == nullptr) {
        return *this; // Nothing to copy
    }

    // Use a temporary stack to reverse order for correct empilha
    PilhaPacotes temp;
    PilhaPacotesNode* currentOther = other.primeiro;
    while (currentOther != nullptr) {
        temp.empilhaPacote(currentOther->pacote); // Empilha Pacote*
        currentOther = currentOther->proximo;
    }

    // Transfer from temporary stack to this stack (maintains original order)
    PilhaPacotesNode* tempCurrent = temp.primeiro;
    PilhaPacotesNode* prev = nullptr;
    while (tempCurrent != nullptr) {
        PilhaPacotesNode* newNode = new PilhaPacotesNode(tempCurrent->pacote);
        if (primeiro == nullptr) {
            primeiro = newNode;
            prev = newNode;
        } else {
            prev->proximo = newNode;
            prev = newNode;
        }
        tamanho++;
        tempCurrent = tempCurrent->proximo;
    }
    // temp's destructor cleans its nodes without affecting 'this' or original Pacotes.
    return *this;
}

Pacote* PilhaPacotes::RemovePacotePorId(int id) {
    if (estaVazia()) return nullptr;

    PilhaPacotesNode* atual = primeiro;
    PilhaPacotesNode* anterior = nullptr;

    while(atual != nullptr && atual->pacote->getIdUnico() != id) {
        anterior = atual;
        atual = atual->proximo;
    }

    if (atual == nullptr) return nullptr; // Not found

    Pacote* pacoteRemovido = atual->pacote;

    if (anterior == nullptr) { // Removing the first node
        primeiro = atual->proximo;
    } else {
        anterior->proximo = atual->proximo;
    }
    
    tamanho--;
    atual->proximo = nullptr; // Disconnect the node
    delete atual; // Delete the node
    return pacoteRemovido; // Return the package pointer
}

Pacote* PilhaPacotes::getPrimeiro() const {
    if (primeiro != nullptr) {
        return primeiro->pacote;
    }
    return nullptr;
}

Pacote* PilhaPacotes::ObterProximoPacote(Pacote* atual) const {
    if (atual == nullptr) {
        // If current is nullptr, return the first package (equivalent to getPrimeiro())
        return getPrimeiro();
    }

    PilhaPacotesNode* current_node = primeiro;
    while (current_node != nullptr) {
        if (current_node->pacote == atual) {
            // Found the current package's node, return the package from the next node
            if (current_node->proximo != nullptr) {
                return current_node->proximo->pacote;
            } else {
                return nullptr; // No next package
            }
        }
        current_node = current_node->proximo;
    }
    return nullptr; // Current package not found in this stack
}

PilhaPacotesNode* PilhaPacotes::getPrimeiroNode() const { return primeiro; }
PilhaPacotesNode* PilhaPacotes::getProximoNode(PilhaPacotesNode* atual) const { return atual->proximo; }