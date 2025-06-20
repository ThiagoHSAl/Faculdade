#include "ListaEncadeadaRota.hpp"
#include "TopologiaArmazens.hpp"
#include <iostream>
#include <string>

RotaNo::RotaNo(int id) : idArmazem(id), proximo(nullptr) {}

ListaEncadeadaRota::ListaEncadeadaRota() : primeiro(nullptr), ultimo(nullptr), atualNaRota(nullptr), tamanho(0) {
}

ListaEncadeadaRota::~ListaEncadeadaRota() {
    RotaNo* atual = primeiro;
    while (atual != nullptr) {
        RotaNo* proximo = atual->proximo;
        delete atual;
        atual = proximo;
    }
    primeiro = nullptr;
    ultimo = nullptr;
    tamanho = 0;
}

void ListaEncadeadaRota::AdicionaArmazem(int id) {
    RotaNo* novoNo = new RotaNo(id);
    if (primeiro == nullptr) {
        primeiro = novoNo;
        ultimo = novoNo;
        atualNaRota = primeiro;
    } else {
        ultimo->proximo = novoNo;
        ultimo = novoNo;
    }
    tamanho++;
}

void ListaEncadeadaRota::InsereNoInicio(int id) {
    RotaNo* novoNo = new RotaNo(id);
    if (primeiro == nullptr) {
        primeiro = novoNo;
        ultimo = novoNo;
        atualNaRota = primeiro;
    } else {
        novoNo->proximo = primeiro;
        primeiro = novoNo;
        atualNaRota = primeiro;
    }
    tamanho++;
}

int ListaEncadeadaRota::GetProximoArmazem() const {
    if (atualNaRota != nullptr && atualNaRota->proximo != nullptr) {
        return atualNaRota->proximo->idArmazem;
    }
    return -1;
}

void ListaEncadeadaRota::Avanca() {
    if (atualNaRota != nullptr) {
        atualNaRota = atualNaRota->proximo;
    }
}

bool ListaEncadeadaRota::EstaNoFinal() const {
    return atualNaRota == ultimo && ultimo != nullptr;
}

int ListaEncadeadaRota::GetTamanho() const {
    return tamanho;
}

ListaEncadeadaRota::ListaEncadeadaRota(const ListaEncadeadaRota& other) :
    primeiro(nullptr), ultimo(nullptr), atualNaRota(nullptr), tamanho(0) {
    RotaNo* atualOther = other.primeiro;
    while (atualOther != nullptr) {
        AdicionaArmazem(atualOther->idArmazem); // Cria novos RotaNo aqui
        atualOther = atualOther->proximo;
    }
    // Lógica para redefinir 'atualNaRota' na nova lista
    if (other.atualNaRota != nullptr) {
        RotaNo* noTemporario = primeiro; // Posição atual na NOVA lista
        RotaNo* otherNoTemporario = other.primeiro; // Posição atual na lista ORIGINAL
        // Avança na NOVA lista e na ORIGINAL até encontrar a posição correspondente
        while (otherNoTemporario != other.atualNaRota && noTemporario != nullptr) {
            otherNoTemporario = otherNoTemporario->proximo;
            noTemporario = noTemporario->proximo;
        }
        atualNaRota = noTemporario; // Define 'atualNaRota' da NOVA lista
    } else {
        atualNaRota = nullptr;
    }
}

ListaEncadeadaRota& ListaEncadeadaRota::operator=(const ListaEncadeadaRota& other) {
    if (this != &other) {
        // Limpar lista atual
        RotaNo* atual = primeiro;
        while (atual != nullptr) {
            RotaNo* proximo = atual->proximo;
            delete atual;
            atual = proximo;
        }
        primeiro = nullptr;
        ultimo = nullptr;
        atualNaRota = nullptr;
        tamanho = 0;
        RotaNo* atualOther = other.primeiro;
        while (atualOther != nullptr) {
            AdicionaArmazem(atualOther->idArmazem);
            atualOther = atualOther->proximo;
        }
        if (other.atualNaRota != nullptr) {
            RotaNo* noTemporario = primeiro;
            RotaNo* otherNoTemporario = other.primeiro;
            while (otherNoTemporario != other.atualNaRota && noTemporario != nullptr) {
                otherNoTemporario = otherNoTemporario->proximo;
                noTemporario = noTemporario->proximo;
            }
            atualNaRota = noTemporario;
        } else {
            atualNaRota = nullptr;
        }
    }
    return *this;
}

RotaNo* ListaEncadeadaRota::GetPrimeiroNo() const {
    return primeiro;
}

RotaNo* ListaEncadeadaRota::GetAtualNaRota() const {
    return atualNaRota;
}

void ListaEncadeadaRota::Imprime() const {
    RotaNo* atual = primeiro;
    while (atual != nullptr) {
        std::cout << atual->idArmazem;
        if (atual->proximo != nullptr) {
            std::cout << " -> ";
        }
        atual = atual->proximo;
    }
    std::cout << std::endl;
}

double ListaEncadeadaRota::CalculaLatenciaRestante(TopologiaArmazens* topologia) const {
    if (atualNaRota == nullptr || atualNaRota->proximo == nullptr) {
        return 0.0;
    }

    double latenciaTotalRestante = 0.0;
    RotaNo* noAtual = atualNaRota;

    while (noAtual != nullptr && noAtual->proximo != nullptr) {
        int idOrigem = noAtual->idArmazem;
        int idDestino = noAtual->proximo->idArmazem;

        Armazem* armazemOrigem = topologia->GetArmazem(idOrigem);
        if (armazemOrigem) {
            SecoesArmazem* secoes = armazemOrigem->GetSecoes();
            if (secoes) {
                TipoCelula* celulaSecao = secoes->EncontraSecao(idDestino);
                if (celulaSecao) {
                    latenciaTotalRestante += celulaSecao->infoAresta.latencia;
                }
            }
        }
        
        noAtual = noAtual->proximo;
    }

    return latenciaTotalRestante;
}

double ListaEncadeadaRota::CalculaLatenciaTotal(TopologiaArmazens* topologia) const {
    // Se a rota não tem pelo menos dois nós, não há trechos para somar a latência.
    if (primeiro == nullptr || primeiro->proximo == nullptr) {
        return 0.0;
    }

    double latenciaTotal = 0.0;
    RotaNo* noAtual = primeiro;

    // Itera por toda a rota para somar a latência de cada trecho.
    while (noAtual != nullptr && noAtual->proximo != nullptr) {
        int idOrigem = noAtual->idArmazem;
        int idDestino = noAtual->proximo->idArmazem;

        // Busca a latência da aresta na topologia.
        Armazem* armazemOrigem = topologia->GetArmazem(idOrigem);
        if (armazemOrigem) {
            SecoesArmazem* secoes = armazemOrigem->GetSecoes();
            if (secoes) {
                TipoCelula* celulaSecao = secoes->EncontraSecao(idDestino);
                if (celulaSecao) {
                    latenciaTotal += celulaSecao->infoAresta.latencia;
                }
            }
        }
        
        noAtual = noAtual->proximo;
    }

    return latenciaTotal;
}