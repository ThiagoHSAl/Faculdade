#ifndef ONIBUS_H
#define ONIBUS_H
#include <string>

struct onibus{
    std::string placa;
    int capacidade_max,lotacao;

    onibus(std::string placa, int quantidade_max);
    void subir_passageiros(int subir);
    void descer_passageiros(int descer);
    void transferir_passageiros(onibus *receptor, int transferir);
    void imprimir_estado();
};
#endif
