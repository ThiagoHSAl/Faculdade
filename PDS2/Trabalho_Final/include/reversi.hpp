#ifndef REVERSI_HPP
#define REVERSI_HPP

#include <iostream>
#include <vector>
#include <string>
#include "board.hpp"
#include "cadastro.hpp"

namespace game{
    class Reversi : public board::Board{
    public:
    Reversi();
    bool currentPlayer;

    //verificação de jogada válida em todas as direções
    bool IsValidDireita(int position);
    bool IsValidEsquerda(int position);
    bool IsValidCima(int position);
    bool IsValidBaixo(int position);
    bool IsValidNordeste(int position);
    bool IsValidSudeste(int position);
    bool IsValidSudoeste(int position);
    bool IsValidNoroeste(int position);
    bool isValidAll(int position);


    bool CanIPlay ();
    void Score (std::string jogador1, std::string jogador2);
    void Inicio();
    void JogarReversi(std::string jogador1, std::string jogador2, cadastro &meucadastro, Reversi &reversi);
    void PrintBoard(std::string jogador1, std::string jogador2);
    int CheckWin(std::string jogador1, std::string jogador2);
    void AnimacaoCaptura();

    // Métodos sobrecarregados da classe base
    void playerMove(int position, bool isPlayer1) override;
    bool CheckTie() override;

    // Método para alternar o jogador
    void CheckGameStatus() override;
    };
}

#endif