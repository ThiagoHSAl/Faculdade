#ifndef BOARD_HPP
#define BOARD_HPP

#include <iostream>
#include <vector>

namespace board {

    class Board {
    protected:
        std::vector<char> board;  // Vetor para armazenar o estado do tabuleiro
        int spaces;
        char player1;
        char player2;

    public:
        // Construtor
        Board(int spaces, char player1, char player2);

        // Métodos setters e getters
        void SetSpaces(int spaces);
        int GetSpaces();
        void SetPlayer1(char player1);
        char GetPlayer1();
        void SetPlayer2(char player2);
        char GetPlayer2();
        void PrintBoard();  // Método para imprimir o tabuleiro
        bool CheckWin();

        // Métodos virtuais puros (para serem implementados nas subclasses)
        virtual void playerMove(int position, bool isPlayer1) = 0;  // Movimento do jogador
        virtual bool CheckTie() = 0;  // Verificação de empate
        virtual void CheckGameStatus() = 0;
    };

}

#endif // BOARD_HPP
