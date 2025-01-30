#include <iostream>
#include <thread>
#include <chrono>
#include <string>
#include <sstream>
#include <limits>
#include <fstream>

void sleep(double i){
    std::this_thread::sleep_for(std::chrono::duration<double>(i));
}


bool validacao_entrada(){
     if (std::cin.fail()) {
        std::cin.clear(); // Limpa o estado de erro do cin
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Descarta entrada inválida
        std::cout << "Entrada invalida, por favor insira apenas numeros!" << std::endl;
        sleep(2);
        return true;
    }
    return false;
}

void limpa_tela(){
    #ifdef _WIN32
        system("cls");  // Comando para limpar o terminal no Windows
    #else
        system("clear");  // Comando para limpar o terminal no Linux/WSL
    #endif
}

bool validacao_fluxo_linha(std::istringstream &fluxo, std::ofstream &erros, std::string &linha) {
    if (fluxo.fail()) { // Verifica estado de erro no fluxo da linha
        erros << "Linha inválida -> " << linha << std::endl;  // Grava a linha no arquivo de erro
        fluxo.clear(); // Limpa o estado de erro
        return false; // Indica que a linha não é válida
    }
    return true; // Indica que a linha é válida
}

bool vazio(std::string &palavra){
    if(palavra.find_first_not_of(" ") == std::string::npos){ //Evita apelidos vazios
        std::cout << "Erro: nome/apelido nao digitado" << std::endl;
        sleep(2);
        return false;
    }
    return true;
}

bool valida_apelido(std::string &linha, std::string &apelido){
    std::istringstream copia(linha); //Evita apelidos com mais de uma palavra
    copia >> apelido;
    if(!vazio(apelido)){
        return false;
    }
    return true;
}