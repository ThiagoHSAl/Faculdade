#include <iostream>
#include <vector>
#include <stdexcept>

class NegativeResultException : public std::exception {
private:
    int valor;
public:
    explicit NegativeResultException(int v) : valor(v) {}
    const char* what() const noexcept override {
        return "Erro: Resultado Negativo.";
    }
    int getValor() const {
        return valor;
    }
};

int main() {
    std::vector<int> valores = {-20, -10, 0, 10, 20};
    
    try {
        int indice;
        std::cin >> indice;
        
        if (indice < 0 || indice >= static_cast<int>(valores.size())) {
            throw std::out_of_range("Erro: Parametro invalido");
        }
        
        int resultado = valores.at(indice);
        
        if (resultado < 0) {
            throw NegativeResultException(resultado);
        } else if (resultado == 0) {
            throw std::logic_error("Erro: O resultado nao deve ser zero");
        }
        
        std::cout << resultado << std::endl;
        
    } catch (const NegativeResultException& e) {
        std::cout << e.what() << std::endl;
        std::cout << e.getValor() << std::endl;
    } catch (const std::exception& e) {
        std::cout << e.what() << std::endl;
    }
    
    return 0;
}