#include "Planejamento.hpp"

SecaoSimulada::SecaoSimulada(int dono, int destino, int cap) {
    idArmazemDono = dono;
    idSecaoDestino = destino;
    capacidade = cap;
    proximo = nullptr;
}

int SecaoSimulada::getTamanhoFuturo() const {
    return pacotesAtuais.getTamanho() + pacotesPrevistos.getTamanho();
}

bool SecaoSimulada::temEspaco(int n = 1) const {
    return (getTamanhoFuturo() + n) <= capacidade;
}

PlanejadorDeCiclo::PlanejadorDeCiclo() : primeira(nullptr), ultima(nullptr) {}

PlanejadorDeCiclo::~PlanejadorDeCiclo() {
    SecaoSimulada* atual = primeira;
    while (atual != nullptr) {
        SecaoSimulada* proximoTemp = atual->proximo;
        delete atual;
        atual = proximoTemp;
    }
}

void PlanejadorDeCiclo::AdicionarSecao(int idDono, int idDestino, int capacidade, const PilhaPacotes& pacotesIniciais) {
    SecaoSimulada* nova = new SecaoSimulada(idDono, idDestino, capacidade);
    nova->pacotesAtuais = pacotesIniciais; // Assume que PilhaPacotes tem um operator=

    if (primeira == nullptr) {
        primeira = nova;
        ultima = nova;
    } else {
        ultima->proximo = nova;
        ultima = nova;
    }
}

SecaoSimulada* PlanejadorDeCiclo::BuscaSecao(int idDono, int idDestino) {
    SecaoSimulada* atual = primeira;
    while (atual != nullptr) {
        if (atual->idArmazemDono == idDono && atual->idSecaoDestino == idDestino) {
            return atual;
        }
        atual = atual->proximo;
    }
    return nullptr;
}