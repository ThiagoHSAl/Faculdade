#ifndef EMPRESA_H
#define EMPRESA_H
#include "onibus.hpp"
#include <iostream>
#include <vector>
#include <string>

struct frota{
int quantidade_onibus;
std::vector<onibus*> minha_frota;

frota();
~frota();
void adicionar_onibus(onibus adicionar);
onibus* buscar_onibus(std::string placa,char print);
void imprimir_estado();
};

#endif
