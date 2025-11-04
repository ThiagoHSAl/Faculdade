#include "ponto.hpp"

// Função para calcular a distância euclidiana entre dois pontos
double Ponto::calcularDistancia(const Ponto& outroPonto) const {
    double dx = static_cast<double>(outroPonto.x - this->x);
    double dy = static_cast<double>(outroPonto.y - this->y);
    return std::sqrt(dx * dx + dy * dy);
}
