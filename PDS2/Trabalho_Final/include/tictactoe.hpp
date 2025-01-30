#include "board.hpp"
#include "cadastro.hpp"
#include <iostream>

namespace game {

    class TicTacToe : public board::Board {
    public:
        bool currentPlayer;  // Representa o jogador atual
        TicTacToe();
        void PrintBoard();
        void playerMove(int position, bool isPlayer1) override;
        bool CheckWin();
        bool CheckTie();
        void CheckGameStatus();
        void RunGame(std::string& jogador1, std::string& jogador2, cadastro& meuCadastro);
    private:
       
        bool gameOver = false;  // Indica se o jogo terminou
        char player1 = 'X';
        char player2 = 'O';
    };

}
