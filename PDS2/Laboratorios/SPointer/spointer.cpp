#include <iostream>
#include <memory>

class Teste {
public:
    int valor;

    // Construtor padrão
    Teste() : valor(0) {
        std::cout << "Construtor " << valor << std::endl;
    }

    // Construtor com valor
    Teste(int v) : valor(v) {
        std::cout << "Construtor " << valor << std::endl;
    }

    // Destruidor
    ~Teste() {
        std::cout << "Destrutor " << valor << std::endl;
    }
};

int main() {
    int n;
    std::cin >> n;

    if (n % 2 == 0) {  // Se n for par
        for (int c = 1; c <= n; ++c) {
            // Criação de um único unique_ptr para garantir a destruição correta
            Teste* teste = new Teste(c);
            std::unique_ptr<Teste> sptr(new Teste(c));
        }
    } else {  // Se n for ímpar
        // shared_ptr inicial
        std::shared_ptr<Teste> sptr1 = std::make_shared<Teste>(0);

        for (int c = 1; c <= n; ++c) {
            // Novo shared_ptr dentro do loop
            std::shared_ptr<Teste> sptr2 = sptr1;  // sptr2 compartilha a posse com sptr1

            // Alterando o valor do objeto compartilhado
            sptr1->valor = c;
        }

        // Exibe a quantidade de shared_ptr que compartilham o mesmo objeto
        std::cout << sptr1.use_count() << std::endl;  // Apenas a contagem, sem "Contagem de shared_ptr:"
    }

    return 0;
}