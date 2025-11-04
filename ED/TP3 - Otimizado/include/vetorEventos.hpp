#ifndef VETOR_EVENTOS_HPP
#define VETOR_EVENTOS_HPP

#include <string>

struct Evento {
    std::string linhaCompleta;
};

class VetorEventos {
private:
    Evento* dados;
    int tamanho;
    int capacidade;

    void redimensionar() {
        capacidade *= 2;
        Evento* novosDados = new Evento[capacidade];
        for (int i = 0; i < tamanho; ++i) {
            novosDados[i] = dados[i];
        }
        delete[] dados;
        dados = novosDados;
    }

public:
    VetorEventos(int capInicial = 100) {
        tamanho = 0;
        capacidade = capInicial;
        dados = new Evento[capacidade];
    }

    ~VetorEventos() {
        delete[] dados;
    }

    void push_back(const Evento& evento) {
        if (tamanho == capacidade) {
            redimensionar();
        }
        dados[tamanho++] = evento;
    }

    Evento& operator[](int indice) {
        return dados[indice];
    }
    
    int getTamanho() const {
        return tamanho;
    }
};

#endif