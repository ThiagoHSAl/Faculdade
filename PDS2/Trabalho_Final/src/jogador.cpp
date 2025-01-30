#include "jogador.hpp"
#include <iostream>
#include <string>
#include <cmath>

//construtor de jogador com nome e apelido
jogador::jogador(std::string nome, std::string apelido) : _nome(nome), _apelido(apelido){
    for(int i=0; i < 3; i++){
        this->vitorias[i] = 0;
        this->derrotas[i] = 0;
    }
}


//construtor de jogador com nome apelido e estatisticas
jogador::jogador(std::string nome, std::string apelido, int vitorias[], int derrotas[]) : _nome(nome), _apelido(apelido){
    for(int i=0; i < 3; i++){
        this->vitorias[i] = vitorias[i];
        this->derrotas[i] = derrotas[i];
    }
}

std::string jogador::GetNome() const{
    return this->_nome;
}

std::string jogador::GetApelido() const {
    return this->_apelido;
}

int jogador::GetVitoria(int jogo) const {
    return this->vitorias[jogo-1];
}

std::string jogador::GetEstatisticas() const { //as estatisticas sao passadas em string pois são usadas para salvar no arquivo txt
    std::string estatisticas="";

    for(int i = 0; i < 3; i++){
        estatisticas += std::to_string(vitorias[i]) + " ";
    }
    for(int i = 0; i < 3; i++){
        estatisticas += std::to_string(derrotas[i]) + " ";
    }

    return estatisticas;
}

void jogador::SetNome(std::string nome){
    this->_nome = nome;
}

void jogador::SetApelido(std::string novoapelido){
    this->_apelido = novoapelido;
}

//Adiciona 1 em vitoria se é positivo e 1 em derrota se é negativo, cada posção do vetor representa um jogo
void jogador::SetEstatistica(int V_D){
    if(V_D > 0){
        V_D--;
        this->vitorias[V_D]++;
    }
    else{
        V_D++;
        this->derrotas[abs(V_D)]++;
    }
}

void jogador::Imprime() const {
    std::cout << this->_apelido << " (" << this->_nome << ")" <<std::endl;
    std::cout << "Vitorias -> ";
    std::cout << "Jogo da velha: " << this->vitorias[0] << " / Lig4: " << this->vitorias[1] << " / Reversi: " << this->vitorias[2];
    std::cout << std::endl;
    std::cout << "Derrotas -> ";
    std::cout << "Jogo da velha: " << this->derrotas[0] << " / Lig4: " << this->derrotas[1] << " / Reversi: " << this->derrotas[2];
    std::cout << std::endl << std::endl;
}