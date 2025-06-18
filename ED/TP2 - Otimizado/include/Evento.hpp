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
            // Se for um evento global (armazem nulo), usa um preenchimento padrão
            // para garantir que a chave de prioridade continue única.
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
        this->pacote = nullptr; // Este evento não se refere a um único pacote
        this->armazemAlvo = armazem;
        this->idSecao = idSecao;
        this->pacotesParaTransportar = pacotes; // Copia a fila de pacotes

        // Gera uma chave de prioridade única
        std::stringstream stringStream;
        stringStream << std::setw(6) << std::setfill('0') << static_cast<int>(tempo)
        << std::setw(3) << std::setfill('0') << armazem->GetIdArmazem()
        << std::setw(3) << std::setfill('0') << idSecao
        << "3"; // Usa um dígito final diferente para garantir unicidade
        this->chavePrioridade = stringStream.str();
    }

    ~Evento() {
    }

    bool operator>(const Evento& other) const {
        return this->chavePrioridade > other.chavePrioridade;
    }
};

#endif