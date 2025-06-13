#ifndef MIN_HEAP_EVENTOS_HPP
#define MIN_HEAP_EVENTOS_HPP

#include "Pacote.hpp"
#include "TopologiaArmazens.hpp"
#include <string>

enum TipoEvento {
    EVENTO_CHEGADA_INICIAL,
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

        Evento(double tempo, TipoEvento t, Pacote* p, Armazem* a);
        Evento(double tempo, TipoEvento t, Armazem* a, int idS);
        
        ~Evento();

        bool operator>(const Evento& other) const {
            return this->chavePrioridade > other.chavePrioridade;
        }
    };

class MinHeapEventos {
private:
    Evento** vetorHeap;
    int capacidade;
    int tamanhoAtual;

    void heapifyDown(int index);
    void heapifyUp(int index);
    void redimensionar();

public:
    MinHeapEventos(int cap = 100);
    ~MinHeapEventos();

    void Insere(Evento* evento);
    Evento* ExtraiMin();
    bool EstaVazia() const;
    int GetTamanho() const;
};

#endif