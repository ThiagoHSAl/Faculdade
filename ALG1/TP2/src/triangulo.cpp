#include "triangulo.hpp"

Triangulo::Triangulo(Arvore a1, Arvore a2, Arvore a3) : perimetro(0), arvore1(a1), arvore2(a2), arvore3(a3) {

    this->perimetro = calcularPerimetroTriangulo();
    // Ordena os índices membros
    if (arvore1.indice > arvore2.indice) {
        std::swap(arvore1.indice, arvore2.indice);
    }
    if (arvore2.indice > arvore3.indice) {
        std::swap(arvore2.indice, arvore3.indice);
    }
    if (arvore1.indice > arvore2.indice) {
        std::swap(arvore1.indice, arvore2.indice);
    }
}

double Triangulo::calcularPerimetroTriangulo() const {
    Ponto vertice1 = arvore1.posicao;
    Ponto vertice2 = arvore2.posicao;
    Ponto vertice3 = arvore3.posicao;
    double lado1 = vertice1.calcularDistancia(vertice2);
    double lado2 = vertice2.calcularDistancia(vertice3);
    double lado3 = vertice3.calcularDistancia(vertice1);
    return lado1 + lado2 + lado3;
}