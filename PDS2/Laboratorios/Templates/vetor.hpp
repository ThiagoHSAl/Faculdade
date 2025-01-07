#include<iostream>
#include<vector>

template <typename T>
class Vetor {
private:
    std::vector<T> _vetor;
    int _tamanho_maximo;  // Tamanho máximo do vetor
    int _num_elementos;   // Número atual de elementos no vetor

public:
    // Construtor que cria um vetor com tamanho máximo igual a 'n'
    Vetor(int n) : _tamanho_maximo(n), _num_elementos(0) {
        _vetor.reserve(n);  // Reservar espaço para n elementos
    }

    // Construtor de cópia
    Vetor(const Vetor<T>& copia) : _vetor(copia._vetor), _tamanho_maximo(copia._tamanho_maximo), _num_elementos(copia._num_elementos) {}

    // Destruidor (não é necessário fazer nada específico, pois o std::vector cuida da memória)
    ~Vetor() {}

    // Define um elemento na posição 'i'
    void SetElemento(int i, T x) {
        if (i >= 0 && i < _tamanho_maximo) {
            if (i >= _num_elementos) {
                _num_elementos = i + 1;
            }
            _vetor[i] = x;
        }
    }

    // Retorna o elemento na posição 'i'
    T GetElemento(int i) {
        if (i >= 0 && i < _num_elementos) {
            return _vetor[i];
        }
        // Se o índice for inválido, retornamos um valor padrão
        return T();  // T() chama o construtor padrão do tipo T
    }

    // Adiciona um elemento ao final do vetor
    void AdicionaElemento(T x) {
        if (_num_elementos < _tamanho_maximo) {
            _vetor.push_back(x);
            _num_elementos++;
        }
    }

    // Imprime todos os elementos do vetor
    void Imprime() {
        for (int i = 0; i < _num_elementos; i++) {
            std::cout << _vetor[i] << " ";
        }
        std::cout << std::endl;
    }
};
