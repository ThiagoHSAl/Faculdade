#include "tictactoe.hpp"
#include "utilidades.hpp"

namespace game {

    TicTacToe::TicTacToe() : board::Board(9, 'X', 'O'), currentPlayer(true) {}

    void TicTacToe::PrintBoard() {
        limpa_tela();
        int position = 0; 
        for (int i = 0; i < spaces; ++i) {
            if (i % 3 == 0 && i != 0) std::cout << "\n---+---+---\n";
            if (board[i] == ' ') {
                std::cout << position;
            } else {
                std::cout << board[i];
            }
            if (i % 3 != 2) {
                std::cout << " | ";
            }
            position++;
        }
        std::cout << "\n";
    }

    void TicTacToe::playerMove(int position, bool isPlayer1) {
        if (position < 0 || position >= spaces) {
            std::cout << "Posição inválida!\n";
            sleep(2);
            return;
        }
        if (board[position] != ' ') {
            std::cout << "Essa posição já está ocupada!\n";
            sleep(2);
            return;
        }
        board[position] = (isPlayer1 ? player1 : player2);
        CheckGameStatus();
    }

    bool TicTacToe::CheckWin() {
        for (int i = 0; i < 3; ++i) {
            if (board[i * 3] != ' ' && board[i * 3] == board[i * 3 + 1] && board[i * 3] == board[i * 3 + 2]) {
                return true;
            }
        }
        for (int i = 0; i < 3; ++i) {
            if (board[i] != ' ' && board[i] == board[i + 3] && board[i] == board[i + 6]) {
                return true;
            }
        }
        if (board[0] != ' ' && board[0] == board[4] && board[0] == board[8]) {
            return true;
        }
        if (board[2] != ' ' && board[2] == board[4] && board[2] == board[6]) {
            return true;
        }
        return false;
    }

    bool TicTacToe::CheckTie() {
        for (int i = 0; i < spaces; ++i) {
            if (board[i] == ' ') {
                return false;  
            }
        }
        return !CheckWin();  
    }

    void TicTacToe::CheckGameStatus() {
        if (CheckWin()) {
            std::cout << "Jogador " << (currentPlayer ? 1 : 2) << " venceu!\n";
            gameOver = true;  
        }
        else if (CheckTie()) {
            std::cout << "Empate!\n";
            gameOver = true;  
        }
        else {
            currentPlayer = !currentPlayer;
        }
    }

    void TicTacToe::RunGame(std::string& jogador1, std::string& jogador2, cadastro& meuCadastro) {
            limpa_tela();
            int position;
            while (!CheckWin() && !CheckTie())
            {
                std::cout << std::endl;
                PrintBoard();
                std::cout << std::endl;
                std::cout << "Jogador " << (currentPlayer ? jogador1 : jogador2) << ", entre com a posição (0-8): ";
                std::cin >> position;

                //evita que position receba char por exemplo
                if (validacao_entrada()) {
                    continue; // Volta para o início do loop
                }

                // Verifica se a posição é válida
                if (position < 0 || position >= 9)
                {
                    std::cout << std::endl;
                    std::cout << "Posição inválida! Tente novamente.\n";
                    sleep(2);
                    continue;
                }

                // Realiza o movimento
                playerMove(position, currentPlayer);

                // Verifica o status do jogo
                if (CheckWin())
                {   
                    PrintBoard();                                    
                    std::cout << std::endl;
                    std::cout << "Jogador " << (currentPlayer ? jogador1 : jogador2) << " venceu!\n";
                    meuCadastro.SetVD(currentPlayer ? jogador1 : jogador2,currentPlayer ? jogador2 : jogador1, 1);
                    sleep(2);
                }
                else if (CheckTie())
                {
                    PrintBoard();
                    std::cout << std::endl;
                    std::cout << "Empate!\n";
                    sleep(2);
                }
            }
    }
}
