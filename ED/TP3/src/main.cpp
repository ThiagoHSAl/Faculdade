#include "gerenciadorRelatorios.hpp"
#include <iostream>
#include <string>
#include <fstream> 

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Uso: " << argv[0] << " <arquivo_de_entrada.txt>" << std::endl;
        return 1; 
    }

    std::string nomeArquivo = argv[1];
    std::ifstream arquivo_entrada(nomeArquivo);

    if (!arquivo_entrada.is_open()) {
        std::cerr << "Erro: Nao foi possivel abrir o arquivo '" << nomeArquivo << "'" << std::endl;
        return 1; 
    }

    GerenciadorRelatorios gerenciador;
    std::string linha;

    while (std::getline(arquivo_entrada, linha)) {
        gerenciador.processarLinha(linha);
    }

    return 0; 
}