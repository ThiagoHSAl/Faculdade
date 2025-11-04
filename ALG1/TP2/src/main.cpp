#include "triangulandia.hpp"
#include <iostream>
#include <iomanip>

int main() {
    std::vector<int> muro;
    std::vector<Arvore> arvores;
    int larguraMuro, numArvores;
    Ponto posicao;

    std::cin >> larguraMuro;
    muro.resize(larguraMuro);
    for (int i = 0; i < larguraMuro; ++i) {
        std::cin >> muro[i];
    }

    std::cin >> numArvores;
    arvores.resize(numArvores);
    for (int i = 0; i < numArvores; ++i) {
        std::cin >> posicao.x >> posicao.y;
        arvores[i].posicao = posicao;
        arvores[i].indice = i + 1;
    }

    Triangulandia triangulandia(muro, arvores);

    int maiorAlturaTriangulo = triangulandia.calcularMaiorAlturaTriangulo();
    std::cout << "Parte 1: " << maiorAlturaTriangulo << std::endl;

    Triangulo menorPerimetro = triangulandia.calcularMenorPerimetro();
    std::cout << std::fixed << std::setprecision(4) << "Parte 2: " << menorPerimetro.getPerimetro() << " " << menorPerimetro.getIndice1() << " " << menorPerimetro.getIndice2() << " " << menorPerimetro.getIndice3() << std::endl;

    return 0;
}
