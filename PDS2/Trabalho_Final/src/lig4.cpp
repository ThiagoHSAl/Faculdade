// lig4.cpp
#include "lig4.hpp"
#include "utilidades.hpp"
#include <iostream>
#include <string>

namespace game{
    Lig4::Lig4() : board::Board(ROWS * COLS, 'X', 'O'), currentPlayer(true), gameOver(false) {
        for(int i = 0; i < ROWS * COLS; i++){
            board[i] = '_'; 
        }
    }

    void Lig4::PrintBoard() {
        for (int i = 0; i < ROWS; i++) {
            for (int j = 0; j < COLS; j++) {
                std::cout << "|" << board[i * COLS + j] << "|";
            }
            std::cout << std::endl;
        }
    }

    int Lig4::findNextEmptyPosition(int col) {
        for (int row = ROWS - 1; row >= 0; row--) { //procura de baixo para cima uma posição válida
            if (board[row * COLS + col] == '_') {
                return row; //retorna (interrompe execução) caso ache posição válida 
            }
        }
        this->colunaCheia[col] = true; //caso não ache posição válida, coluna está cheia  
        return -1; 
    }

    void Lig4::playerMove(int position, bool currentPlayer) {
        if (position < 1 || position > COLS) { //checa se coluna é válida
            std::cout << "Erro: coluna inválida\n";
            return;
        }

        int col = position - 1; 
        int row = findNextEmptyPosition(col); //atribui a posição válida mais baixa na coluna

        if (row == -1) { //checa se a coluna escolhida está cheia
            std::cout << "Erro: coluna cheia\n";
            return; //interrompe a execução 
        }

        board[row * COLS + col] = (this->currentPlayer ? player1 : player2); //atualiza o tabuleiro
        this->CheckGameStatus(); //verifica vitória, empate ou continua o jogo
    }

    bool Lig4::CheckWin() { //procura uma sequência de 4 peças iguais em qualquer direção
        char playerSymbol = currentPlayer ? player1 : player2;

        // Horizontal
        for (int i = 0; i < ROWS; i++) {
            for (int j = 0; j <= COLS - 4; j++) {
                if (board[i * COLS + j] == playerSymbol &&
                    board[i * COLS + j + 1] == playerSymbol &&
                    board[i * COLS + j + 2] == playerSymbol &&
                    board[i * COLS + j + 3] == playerSymbol) {
                    return true;
                }
            }
        }

        // Vertical
        for (int i = 0; i <= ROWS - 4; i++) {
            for (int j = 0; j < COLS; j++) {
                if (board[i * COLS + j] == playerSymbol &&
                    board[(i + 1) * COLS + j] == playerSymbol &&
                    board[(i + 2) * COLS + j] == playerSymbol &&
                    board[(i + 3) * COLS + j] == playerSymbol) {
                    return true;
                }
            }
        }

        // Diagonal (descendente)
        for (int i = 0; i <= ROWS - 4; i++) {
            for (int j = 0; j <= COLS - 4; j++) {
                if (board[i * COLS + j] == playerSymbol &&
                    board[(i + 1) * COLS + j + 1] == playerSymbol &&
                    board[(i + 2) * COLS + j + 2] == playerSymbol &&
                    board[(i + 3) * COLS + j + 3] == playerSymbol) {
                    return true;
                }
            }
        }

        // Diagonal (ascendente)
        for (int i = 3; i < ROWS; i++) {
            for (int j = 0; j <= COLS - 4; j++) {
                if (board[i * COLS + j] == playerSymbol &&
                    board[(i - 1) * COLS + j + 1] == playerSymbol &&
                    board[(i - 2) * COLS + j + 2] == playerSymbol &&
                    board[(i - 3) * COLS + j + 3] == playerSymbol) {
                    return true;
                }
            }
        }

        return false; //caso não haja vitória, retorna falso
    }

    bool Lig4::CheckTie() { //checa se todas as colunas estão cheias (e não houve vitória)
        for(int i = 0; i < COLS; i++){
            if(!this->colunaCheia[i]){
                return false;
            }
        }

        return true;
    }

    void Lig4::CheckGameStatus() {
        if (CheckWin()) { //verifica vitória
            limpa_tela();
            PrintBoard();
            std::cout << "Jogador " << (this->currentPlayer ? 1 : 2) << " venceu!\n";
            sleep(2);
            gameOver = true; //indica que o jogo acabou
        }
        else if (CheckTie()) { //caso não haja vitória, verifica empate
            limpa_tela();
            PrintBoard();
            std::cout << "Empate!\n";
            sleep(2);
            gameOver = true; //indica que o jogo acabou
        }
        else { //caso não haja vitória ou empate, alterna a jogada e continua o jogo
            this->currentPlayer = !this->currentPlayer;
        }
    }

    void Lig4::runGame(std::string& jogador1, std::string& jogador2, cadastro& meuCadastro){
        int jogada;

        while (true) { //loop principal do jogo
            limpa_tela();
            this->PrintBoard();
            
            std::cout << "Jogador " << (this->currentPlayer ? jogador1 : jogador2) 
            << ", faça sua jogada (1-7): ";
            std::cin >> jogada; //lê a jogada
            if(validacao_entrada()){
                continue;
            }
            
            this->playerMove(jogada, this->currentPlayer); //executa a jogada
    
            if (this->gameOver) {//checa se o jogo acabou
                this->currentPlayer? 
                    meuCadastro.SetVD(jogador1, jogador2, 2) : 
                    meuCadastro.SetVD(jogador2, jogador1, 2);
                this->PrintBoard();
                break; //finaliza o jogo
            }
            
        }
    }
}