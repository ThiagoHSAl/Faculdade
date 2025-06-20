#include <iostream>
#include <fstream>
#include "TopologiaArmazens.hpp"
#include "Transporte.hpp"
#include "Escalonador.hpp"
#include "Pacote.hpp"
#include <chrono> 

int main(int argc, char** argv) {
    // --- Bloco 1: Leitura dos Parâmetros da Simulação ---
    auto start_time = std::chrono::high_resolution_clock::now();
    int capacidade;
    double latencia, intervalo, custo;
    int capacidadeSecaoArmazenamento;

    if (argc != 2) {
        std::cerr << "Erro: É necessário fornecer o nome do arquivo como argumento." << std::endl;
        return 1;
    }

    std::string nomeArquivo = argv[1];
    std::ifstream arquivo(nomeArquivo);
    if (!arquivo.is_open()) {
        std::cerr << "Erro: Não foi possível abrir o arquivo " << nomeArquivo << std::endl;
        return 1;
    }

    arquivo >> intervalo;
    arquivo >> custo;
    arquivo >> capacidadeSecaoArmazenamento;

    // --- Bloco 2: Leitura e Construção da Topologia ---
    int numeroArmazens;
    arquivo >> numeroArmazens;


    // Ler matriz de latência
    double** matrizLatencia = new double*[numeroArmazens];
    for (int i = 0; i < numeroArmazens; ++i) {
        matrizLatencia[i] = new double[numeroArmazens];
        for (int j = 0; j < numeroArmazens; ++j) {
            arquivo >> matrizLatencia[i][j];
        }
    }

    // Ler matriz de capacidade
    int** matrizCapacidade = new int*[numeroArmazens];
    for (int i = 0; i < numeroArmazens; ++i) {
        matrizCapacidade[i] = new int[numeroArmazens];
        for (int j = 0; j < numeroArmazens; ++j) {
            arquivo >> matrizCapacidade[i][j];
        }
    }

    TopologiaArmazens* topologia = new TopologiaArmazens(numeroArmazens, matrizCapacidade, matrizLatencia);
    Transporte* sistemaTransporte = new Transporte(topologia, custo, intervalo, capacidadeSecaoArmazenamento);
    
    for (int i = 0; i < numeroArmazens; ++i) {
        delete[] matrizLatencia[i];
        delete[] matrizCapacidade[i];
    }
    delete[] matrizCapacidade;
    delete[] matrizLatencia;

    // --- Bloco 3: Leitura e Criação dos Pacotes ---
    int numeroPacotes;
    arquivo >> numeroPacotes;

    Pacote** todosPacotes = new Pacote*[numeroPacotes];

    for (int i = 0; i < numeroPacotes; ++i) {
        double timestamp;
        int id, origem, destino;
        char junk_word[4]; 

        arquivo >> timestamp >> junk_word >> id >> junk_word >> origem >> junk_word >> destino;
        
        Pacote* pacote = new Pacote();
        pacote->setTimestampPostagem(timestamp);
        pacote->setIdUnico(id);
        pacote->setArmazemOrigem(origem);
        pacote->setArmazemDestino(destino);

        todosPacotes[i] = pacote;
    }

    // --- Bloco 4: Execução da Simulação ---
    Escalonador* escalonador = new Escalonador(topologia, sistemaTransporte, numeroPacotes);
    
    escalonador->InicializaSimulacao(todosPacotes, numeroPacotes);
    escalonador->RodaSimulacao();
    //topologia->ImprimeEstatisticasFinais();
    // --- Bloco 5: Limpeza de Memória ---
    for (int i = 0; i < numeroPacotes; ++i) {
        delete todosPacotes[i];
    }
    
    delete[] todosPacotes;

    delete escalonador;
    delete sistemaTransporte;
    delete topologia;

    auto end_time = std::chrono::high_resolution_clock::now(); // 

    // Calcula a duração
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time); // 
    /*
    // Imprime o tempo de execução (Exemplo: ao final da saída, ou como uma estatística final)
    std::cout << "\n--- ESTATISTICAS DE DESEMPENHO ---" << std::endl;
    std::cout << "Tempo de Execucao da Simulacao: " << duration.count() << " micro s" << std::endl; // 
    std::cout << "------------------------------------" << std::endl;*/

    return 0;
}