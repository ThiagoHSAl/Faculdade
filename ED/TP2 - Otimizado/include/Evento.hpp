#ifndef EVENTO_HPP
#define EVENTO_HPP

#include "Pacote.hpp"
#include "Fila.hpp"
#include "TopologiaArmazens.hpp"
#include <string>
#include <iomanip>
#include <sstream>

enum TipoEvento {
    EVENTO_CHEGADA_INICIAL,
    EVENTO_PREVISAO_TRANSPORTE,
    EVENTO_INICIA_TRANSPORTE,
    EVENTO_ARMAZENAMENTO
};

struct Evento {
    double tempoOcorrencia;
    TipoEvento tipo;
    Pacote* pacote;
    Armazem* armazemAlvo;
    int idSecao;
    std::string chavePrioridade;
    Fila<Pacote*> pacotesParaTransportar;

    Evento(double tempo, TipoEvento tipoEvento, Pacote* pacote, Armazem* armazem) {
        this->tempoOcorrencia = tempo;
        this->tipo = tipoEvento;
        this->pacote = pacote;
        this->armazemAlvo = armazem;
        this->idSecao = -1; 

        std::stringstream stringStream;
        stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo)
        << std::setw(6) << std::setfill('0') << pacote->getIdUnico()
        << "1";
        this->chavePrioridade = stringStream.str();
    }

    Evento(double tempo, TipoEvento tipoEvento, Armazem* armazem, int idSecao) {
        this->tempoOcorrencia = tempo;
        this->tipo = tipoEvento;
        this->pacote = nullptr;
        this->armazemAlvo = armazem;
        this->idSecao = idSecao;

        std::stringstream stringStream;
        stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo);
        
        if (armazem != nullptr) {
        stringStream << std::setw(3) << std::setfill('0') << armazem->GetIdArmazem()
                    << std::setw(3) << std::setfill('0') << idSecao;
        } else {
            stringStream << "000" << "000";
        }

        stringStream << "2";
        this->chavePrioridade = stringStream.str();
    }

    Evento(const Evento& other) {
        this->tempoOcorrencia = other.tempoOcorrencia;
        this->tipo = other.tipo;
        this->armazemAlvo = other.armazemAlvo;
        this->idSecao = other.idSecao;
        this->chavePrioridade = other.chavePrioridade;

        if (other.pacote != nullptr) {
            this->pacote = new Pacote(*(other.pacote));
        } else {
            this->pacote = nullptr;
        }
    }

    Evento(double tempo, TipoEvento tipoEvento, Armazem* armazem, int idSecao, Fila<Pacote*>& pacotes) {
        this->tempoOcorrencia = tempo;
        this->tipo = tipoEvento;
        this->pacote = nullptr; 
        this->armazemAlvo = armazem;
        this->idSecao = idSecao;
        this->pacotesParaTransportar = pacotes; 

        std::stringstream stringStream;
        stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo)
        << std::setw(3) << std::setfill('0') << armazem->GetIdArmazem()
        << std::setw(3) << std::setfill('0') << idSecao
        << "3"; 
        this->chavePrioridade = stringStream.str();
    }

    ~Evento() {
    }

    bool operator>(const Evento& other) const {
        return this->chavePrioridade > other.chavePrioridade;
    }

    void Imprime() const {
    std::cout << "  - Evento: T=" << this->tempoOcorrencia;
    std::cout << " | Tipo: ";
    switch (this->tipo) {
        case EVENTO_CHEGADA_INICIAL: std::cout << "CHEGADA_INICIAL"; break;
        case EVENTO_ARMAZENAMENTO: std::cout << "ARMAZENAMENTO"; break;
        case EVENTO_PREVISAO_TRANSPORTE: std::cout << "PREVISAO_TRANSPORTE"; break;
        case EVENTO_INICIA_TRANSPORTE: std::cout << "INICIA_TRANSPORTE"; break;
        default: std::cout << "DESCONHECIDO"; break;
    }
    if(this->pacote != nullptr) {
        std::cout << " | Pacote: " << this->pacote->getIdUnico();
    }
    if(this->armazemAlvo != nullptr) {
        std::cout << " | Armazem: " << this->armazemAlvo->GetIdArmazem();
    }
    if(this->idSecao != -1) {
        std::cout << " | Secao: " << this->idSecao;
    }
    std::cout << std::endl;
}
};

#endif