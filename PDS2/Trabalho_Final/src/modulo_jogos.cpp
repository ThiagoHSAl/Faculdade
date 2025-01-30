#include <string>
#include "tictactoe.hpp"
#include "reversi.hpp"
#include "lig4.hpp"
#include "modulo_cadastro.hpp"
#include "utilidades.hpp"


int modulo_jogos(std::string jogador1, std::string jogador2, cadastro &meucadastro){
    limpa_tela();
    std::cout << "====================================\n";
    std::cout << "Jogadores encontrados!!!\n";
    std::cout << "Jogador 1: " << jogador1 << "\nJogador 2: " << jogador2 << "\n";
    std::cout << "====================================\n";
    sleep(3);

    int comando;
    while (comando != 5)
    {
        limpa_tela();
        std::cout << "====================================\n";
        std::cout << "Escolha Qual Jogo Deseja: \n";
        std::cout << "1 - Jogo da Velha\n";
        std::cout << "2 - Lig4\n";
        std::cout << "3 - Reversi\n";
        std::cout << "4 - Ir para o menu de cadastros\n";
        std::cout << "5 - Voltar para o menu inicial\n";
        std::cout << "6 - Exibir Ranking\n";
        std::cout << "7 - Sair\n";
        std::cout << "Digite a opção desejada: ";
        std::cin >> comando;
        
        //evita que comando receba char por exemplo
        if (validacao_entrada()) {
            continue; // Volta para o início do loop
        }

        //Jogar jogo da velha
        if (comando == 1)
        {
            game::TicTacToe games;
            games.RunGame(jogador1, jogador2, meucadastro);
        }

        else if (comando == 2){
            game::Lig4 lig4;
            lig4.runGame(jogador1, jogador2, meucadastro);    
        }

        //Jogar Reversi
        else if (comando == 3){
            game::Reversi reversi;
            reversi.JogarReversi(jogador1, jogador2, meucadastro, reversi);
        }

        //Retorna 2 para o menu anterior, que troca para o menu de cadastros
        else if (comando == 4){
            return 2;
        }

        //Retorna 1 ao menu anterior, que mantém a execução do programa
        else if (comando == 5){
            return 1;
        }

        else if (comando == 6){
            meucadastro.Ranking();    
        }

        //Retorna 3 ao menu anterior, que finaliza o programa
        else if (comando == 7){
        return 3;
        }

        else{
            std::cout << "ERRO: Opção Inválida!!\n";
        }
    }
    return 1;
}
    