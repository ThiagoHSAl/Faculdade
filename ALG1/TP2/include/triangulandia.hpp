#ifndef TRIANGULANDIA_HPP
#define TRIANGULANDIA_HPP
#include <vector>
#include <limits>
#include "ponto.hpp"
#include "triangulo.hpp"


class Triangulandia {
public:
    Triangulandia(std::vector<int> muro, std::vector<Arvore> arvores);
    Triangulo calcularMenorPerimetro();
    int calcularMaiorAlturaTriangulo() const;

private:
    std::vector<int> muro;
    std::vector<Arvore> arvores;
    Triangulo menorPerimetroRecursivo(int esquerda, int direita);
};

#endif // TRIANGULANDIA_HPP