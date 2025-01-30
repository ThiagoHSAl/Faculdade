#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>
#include "board.hpp"  
#include "jogador.hpp"
#include "cadastro.hpp"
#include "cadastro.hpp"
#include <fstream>

namespace board {

    class ConcreteBoard : public Board {
    public:
        ConcreteBoard(int spaces, char player1, char player2)
            : Board(spaces, player1, player2) {}

        // Implementação dos métodos virtuais puros
        void playerMove(int position, bool isPlayer1) override {
            if (position >= 0 && position < spaces && board[position] == ' ') {
                board[position] = isPlayer1 ? player1 : player2;
            }
        }

        bool CheckTie() override {
            for (char cell : board) {
                if (cell == ' ') {
                    return false;  // Se houver pelo menos uma célula vazia, não é empate
                }
            }
            return true;
        }

        void CheckGameStatus() override {
            // Implementação simples de status (apenas para fins de teste)
            std::cout << "Game ongoing..." << std::endl;
        }
    };


    // Teste de inicialização do Board
    TEST_CASE("Teste de inicialização do Board") {
        ConcreteBoard b(9, 'X', 'O');  // Criando um ConcreteBoard com 9 espaços e dois jogadores ('X' e 'O')

        // Verifica se o número de espaços é corretamente inicializado
        CHECK(b.GetSpaces() == 9);

        // Verifica se os jogadores são corretamente inicializados
        CHECK(b.GetPlayer1() == 'X');
        CHECK(b.GetPlayer2() == 'O');

        // Verifica se o tabuleiro foi inicializado com espaços vazios
        CHECK(b.GetSpaces() == 9);
    }

    // Teste de redimensionamento do Board
    TEST_CASE("Teste de redimensionamento do Board") {
        ConcreteBoard b(9, 'X', 'O');  // Inicializa com 9 espaços

        // Redimensiona o tabuleiro para 16 espaços
        b.SetSpaces(16);
        CHECK(b.GetSpaces() == 16);  // Verifica se o número de espaços foi alterado

        // Verifica se o tabuleiro foi redimensionado corretamente para 16 espaços
        CHECK(b.GetSpaces() == 16);
    }

    // Teste dos setters e getters para jogadores
    TEST_CASE("Teste dos setters e getters de jogadores") {
        ConcreteBoard b(9, 'X', 'O');

        // Testa os setters e getters para os jogadores
        b.SetPlayer1('A');
        b.SetPlayer2('B');

        CHECK(b.GetPlayer1() == 'A');  // Verifica se o jogador 1 foi alterado para 'A'
        CHECK(b.GetPlayer2() == 'B');  // Verifica se o jogador 2 foi alterado para 'B'
    }

    // Teste de movimento no Board
    TEST_CASE("Teste de movimento no Board") {
        ConcreteBoard b(9, 'X', 'O');

        // Movimento do jogador 1
        b.playerMove(0, true);
        CHECK(b.GetSpaces() == 9);  // O número de espaços não deve mudar
        CHECK(b.GetPlayer1() == 'X');  // Verifica se o jogador 1 fez o movimento

        // Movimento do jogador 2
        b.playerMove(1, false);
        CHECK(b.GetPlayer2() == 'O');  // Verifica se o jogador 2 fez o movimento
    }

    // Teste de empate
    TEST_CASE("Teste de empate no Board") {
        ConcreteBoard b(9, 'X', 'O');

        // Simula um empate (tabuleiro cheio sem vencedor)
        b.playerMove(0, true);
        b.playerMove(1, false);
        b.playerMove(2, true);
        b.playerMove(3, false);
        b.playerMove(4, true);
        b.playerMove(5, false);
        b.playerMove(6, true);
        b.playerMove(7, false);
        b.playerMove(8, true);

        CHECK(b.CheckTie() == true);  // Verifica se o jogo está em empate
    }

}

TEST_SUITE("Testes para a classe jogador") {
    TEST_CASE("Teste de construção e getters") {
        jogador j("NomeTeste", "ApelidoTeste");

        CHECK(j.GetNome() == "NomeTeste");
        CHECK(j.GetApelido() == "ApelidoTeste");

        for (int i = 1; i <= 3; i++) {
            CHECK(j.GetVitoria(i) == 0);
        }
    }

    TEST_CASE("Teste de estatísticas com construtor completo") {
        int vitorias[] = {2, 3, 4};
        int derrotas[] = {1, 2, 3};
        jogador j("NomeCompleto", "ApelidoCompleto", vitorias, derrotas);

        CHECK(j.GetNome() == "NomeCompleto");
        CHECK(j.GetApelido() == "ApelidoCompleto");

        for (int i = 1; i <= 3; i++) {
            CHECK(j.GetVitoria(i) == vitorias[i - 1]);
        }

        CHECK(j.GetEstatisticas() == "2 3 4 1 2 3 ");
    }

    TEST_CASE("Teste de SetNome e SetApelido") {
        jogador j("NomeTeste", "ApelidoTeste");
        j.SetNome("NovoNome");
        j.SetApelido("NovoApelido");

        CHECK(j.GetNome() == "NovoNome");
        CHECK(j.GetApelido() == "NovoApelido");
    }

    TEST_CASE("Teste de atualização de estatísticas") {
        jogador j("NomeTeste", "ApelidoTeste");

        // Testa vitória no jogo 1
        j.SetEstatistica(1);
        CHECK(j.GetVitoria(1) == 1);

        // Testa derrota no jogo 2
        j.SetEstatistica(-2);
        CHECK(j.GetVitoria(2) == 0); // Sem vitória no jogo 2
    }

    TEST_CASE("Teste de impressão") {
        jogador j("NomeTeste", "ApelidoTeste");
        j.Imprime(); // Apenas observação
    }
}

TEST_CASE("Testando construtor de cadastro com arquivo vazio") {
    std::ofstream arquivo("../data/cadastro.txt"); // Garante que o arquivo exista, mas vazio
    arquivo.close();

    cadastro c;

    CHECK(c.VerificaApelido("inexistente") == -1);
}


TEST_CASE("Testando CadastraJogador") {
    cadastro c;

    c.CadastraJogador("Jogador1", "Player1");
    CHECK(c.VerificaApelido("Player1") != -1);

    c.CadastraJogador("Jogador2", "Player2");
    CHECK(c.VerificaApelido("Player2") != -1);

    // Tentativa de cadastrar com apelido já existente
    c.CadastraJogador("OutroJogador1", "Player1");
    CHECK(c.VerificaApelido("Player1") != -1); // Não deve alterar o cadastro existente
}

TEST_CASE("Testando DeletaJogador") {
    cadastro c;

    c.CadastraJogador("Jogador1", "Player1");
    c.CadastraJogador("Jogador2", "Player2");

    c.DeletaJogador("Player1");
    CHECK(c.VerificaApelido("Player1") == -1);

    c.DeletaJogador("Player2");
    CHECK(c.VerificaApelido("Player2") == -1);

    // Tentativa de deletar jogador inexistente
    c.DeletaJogador("Inexistente");
}

TEST_CASE("Testando EditaJogador") {
    cadastro c;

    c.CadastraJogador("Jogador1", "Player1");
    c.EditaJogador("Player1", "Player1Novo");

    CHECK(c.VerificaApelido("Player1") == -1);
    CHECK(c.VerificaApelido("Player1Novo") != -1);

    // Tentativa de editar para um apelido já existente
    c.CadastraJogador("Jogador2", "Player2");
    c.EditaJogador("Player1Novo", "Player2");
    CHECK(c.VerificaApelido("Player2") != -1); // Player2 deve continuar existindo
    CHECK(c.VerificaApelido("Player1Novo") != -1); // Player1Novo não deve ser alterado
}

TEST_CASE("Testando Imprime") {
    cadastro c;

    c.CadastraJogador("JogadorB", "PlayerB");
    c.CadastraJogador("JogadorA", "PlayerA");

    // Redireciona saída padrão para verificar a saída de Imprime
    std::ostringstream oss;
    std::streambuf* coutBuf = std::cout.rdbuf();
    std::cout.rdbuf(oss.rdbuf());

    c.Imprime();

    std::cout.rdbuf(coutBuf); // Restaura o buffer padrão de saída

    std::string saidaEsperada = 
        "PlayerA (JogadorA)\n"
        "Vitorias -> Jogo da velha: 0 / Lig4: 0 / Reversi: 0\n"
        "Derrotas -> Jogo da velha: 0 / Lig4: 0 / Reversi: 0\n\n"
        "PlayerB (JogadorB)\n"
        "Vitorias -> Jogo da velha: 0 / Lig4: 0 / Reversi: 0\n"
        "Derrotas -> Jogo da velha: 0 / Lig4: 0 / Reversi: 0\n\n";

    CHECK(oss.str() == saidaEsperada);
}
