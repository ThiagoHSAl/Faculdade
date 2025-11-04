#include "triangulandia.hpp"
#include <cmath>
#include <limits>  
#include <stdexcept>
#include <vector>
#include "mergesort.hpp"

#define INF std::numeric_limits<int>::max()
#define NUMERO_MAXIMO_VIZINHOS 15


Triangulandia::Triangulandia(std::vector<int> muro, std::vector<Arvore> arvores)
    : muro(std::move(muro)), arvores(std::move(arvores)) {

} 


Triangulo Triangulandia::menorPerimetroRecursivo(int esquerda, int direita) {
    if (direita - esquerda < 2) {
        return Triangulo();
    }

    int meio = esquerda + (direita - esquerda) / 2;
    Triangulo menorTrianguloEsquerda = menorPerimetroRecursivo(esquerda, meio);
    Triangulo menorTrianguloDireita = menorPerimetroRecursivo(meio + 1, direita);
    Triangulo menorTriangulo = std::min(menorTrianguloEsquerda, menorTrianguloDireita);

    std::vector<Arvore> faixa;
    double meioX = arvores[meio].posicao.x;
    for (int i = esquerda; i <= direita; ++i) {
        if (std::abs(arvores[i].posicao.x - meioX) < menorTriangulo.perimetro / 2) {
            faixa.push_back(arvores[i]);
        }
    }

    mergeSort(faixa, comparaPorY);

    size_t tamanhoFaixa = faixa.size();
    for (size_t i = 0; i < tamanhoFaixa; ++i) {
        for (size_t j = i + 1; j < i + NUMERO_MAXIMO_VIZINHOS && j < tamanhoFaixa; ++j) {
            for (size_t k = j + 1; k < i + NUMERO_MAXIMO_VIZINHOS && k < tamanhoFaixa; ++k) {
                Triangulo trianguloAtual(faixa[i], faixa[j], faixa[k]);
                if (trianguloAtual < menorTriangulo) {
                    menorTriangulo = trianguloAtual;
                }
            }
        }
    }

    return menorTriangulo;
}

Triangulo Triangulandia::calcularMenorPerimetro() {
    int numArvores = static_cast<int>(arvores.size());
    if (numArvores < 3) {
        throw std::runtime_error("Número insuficiente de árvores para formar um triângulo.");
    } 
    mergeSort(arvores, comparaPorX);
    Triangulo menorPerimetro = menorPerimetroRecursivo(0, numArvores - 1);
    return menorPerimetro;
}


// Calcula a maior altura de um triângulo isósceles que pode ser formado no muro sem adicionar nenhum bloco
int Triangulandia::calcularMaiorAlturaTriangulo() const {
    size_t tamanhoMuro = muro.size();
    std::vector<int> maiorRampaDeSubida(tamanhoMuro, INF), maiorRampaDeDescida(tamanhoMuro, INF), maiorAlturaTriangulo(tamanhoMuro, 0);

    maiorRampaDeSubida[0] = 1;
    maiorRampaDeDescida[tamanhoMuro - 1] = 1;
    
    int maiorAlturaTrianguloGeral = 0;

    // A maior rampa de subida a partir de i é 1 unidade maior que a anterior ou limitada pela altura do muro
    for (size_t i = 1; i < tamanhoMuro; ++i) {
        maiorRampaDeSubida[i] = std::min(maiorRampaDeSubida[i - 1] + 1, muro[i]);
    }

    // A maior rampa de descida a partir de i é 1 unidade maior que a próxima ou limitada pela altura do muro
    for (int i = static_cast<int>(tamanhoMuro - 2); i >= 0; --i) {
        maiorRampaDeDescida[i] = std::min(maiorRampaDeDescida[i + 1] + 1, muro[i]);
    }

    // A maior altura do triângulo a partir de cada posição é o mínimo entre a maior rampa de subida e a maior rampa de descida
    for (size_t i = 0; i < tamanhoMuro; ++i) {
        maiorAlturaTriangulo[i] = std::min(maiorRampaDeSubida[i], maiorRampaDeDescida[i]);
        
        if (maiorAlturaTriangulo[i] > maiorAlturaTrianguloGeral) {
            maiorAlturaTrianguloGeral = maiorAlturaTriangulo[i];
        }
    }

    return maiorAlturaTrianguloGeral;
}   