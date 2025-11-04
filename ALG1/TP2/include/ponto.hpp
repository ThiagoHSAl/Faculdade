#ifndef PONTO_HPP
#define PONTO_HPP
#include <cmath>

struct Ponto {
    int x;
    int y;
    double calcularDistancia(const Ponto& outroPonto) const;
};

struct Arvore {
    Ponto posicao;
    int indice;
    Arvore() : posicao({0, 0}), indice(0) {}
};

#endif // PONTO_HPP