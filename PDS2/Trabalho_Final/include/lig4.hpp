#ifndef LIG4_HPP
#define LIG4_HPP

#include "board.hpp"
#include "cadastro.hpp"
#include <map>

namespace game{ 

class Lig4 : public board::Board {
    private:
        static const int ROWS = 6;
        static const int COLS = 7;
        bool currentPlayer;
        bool gameOver;
        std::map<int, bool> colunaCheia;

        // Método auxiliar para encontrar a próxima posição vazia em uma coluna
        int findNextEmptyPosition(int col);

    public:
        Lig4(); // Construtor
        void PrintBoard();
        void playerMove(int position, bool isPlayer1) override;
        bool CheckWin();
        bool CheckTie() override;
        void CheckGameStatus() override;
        void runGame(std::string& jogador1, std::string& jogador2, cadastro& meuCadastro);
    };

}
    
#endif

