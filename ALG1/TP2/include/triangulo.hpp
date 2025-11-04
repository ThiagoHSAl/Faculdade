#ifndef TRIANGULO_HPP
#define TRIANGULO_HPP
#include <utility>
#include <limits>
#include "ponto.hpp"

#define DOUBLE_INF std::numeric_limits<double>::max()

class Triangulo {
    public:
    double calcularPerimetroTriangulo() const;
    double getPerimetro() const {
        return perimetro;
    }

    int getIndice1() const {    
        return arvore1.indice;
    }

    int getIndice2() const {    
        return arvore2.indice;
    }

    int getIndice3() const {    
        return arvore3.indice;
    }

    bool operator<(const Triangulo& outro) const {
    
        // Define uma pequena tolerância para comparação de 'double'
        const double EPSILON = 1e-9; 
    
        // 1. Critério principal: Perímetro
        // Só retorne 'true' se 'this->perimetro' for SIGNIFICATIVAMENTE menor
        if (this->perimetro < outro.perimetro - EPSILON) {
            return true;
        }
        // Só retorne 'false' se 'this->perimetro' for SIGNIFICATIVAMENTE maior
        if (this->perimetro > outro.perimetro + EPSILON) {
            return false;
        }
    
        // --- Se os perímetros forem "iguais" (dentro da tolerância EPSILON) ---
        // Prossiga para o desempate lexicográfico
        
        // 2. Critério de desempate 1: arvore1.indice
        if (this->arvore1.indice < outro.arvore1.indice) {
            return true;
        }
        if (this->arvore1.indice > outro.arvore1.indice) {
            return false;
        }
    
        // 3. Critério de desempate 2: arvore2.indice
        if (this->arvore2.indice < outro.arvore2.indice) {
            return true;
        }
        if (this->arvore2.indice > outro.arvore2.indice) {
            return false;
        }
    
        // 4. Critério de desempate 3: arvore3.indice
        return this->arvore3.indice < outro.arvore3.indice;
    }

    private:
    double perimetro;
    Arvore arvore1;
    Arvore arvore2;
    Arvore arvore3;
    
      // Construtor "Default" (para criar Triangulo.Infinito)
    Triangulo() : perimetro(DOUBLE_INF), arvore1(), arvore2(), arvore3() {}
    // Construtor que ordena os índices
    Triangulo(Arvore a1, Arvore a2, Arvore a3);
    
    friend class Triangulandia;
};

#endif // TRIANGULO_HPP