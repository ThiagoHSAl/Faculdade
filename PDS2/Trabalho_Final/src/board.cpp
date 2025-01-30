#include "board.hpp"
#include <iostream>

namespace board {

    Board::Board(int spaces, char player1, char player2)
        : spaces(spaces), player1(player1), player2(player2) {
        board.resize(spaces, ' ');  // Inicializa o vetor 'board' com espaços vazios (' ')
    }

    void Board::SetSpaces(int spaces) {
        this->spaces = spaces;
        board.resize(spaces, ' ');  // Redimensiona o tabuleiro e preenche com espaços vazios
    }

    int Board::GetSpaces() {
        return spaces;
    }

    void Board::SetPlayer1(char player1) {
        this->player1 = player1;
    }

    char Board::GetPlayer1() {
        return player1;
    }

    void Board::SetPlayer2(char player2) {
        this->player2 = player2;
    }

    char Board::GetPlayer2() {
        return player2;
    }
}
