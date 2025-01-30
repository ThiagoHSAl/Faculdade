#include "reversi.hpp"
#include "utilidades.hpp"

namespace game{
    
        Reversi::Reversi() : board::Board(64, 'X', 'O'), currentPlayer(true){//Constrói um tabuleiro 8x8 e seta X e O para os players
    }

    bool Reversi::IsValidDireita(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção à direita
        if (position % 8 < 7 && board[position + 1] == opponent) {
            int tempPos = position + 1;
            while (tempPos % 8 < 7) { // Continua verificando na mesma linha
                tempPos++;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }
        return valid;
    }

    bool Reversi::IsValidEsquerda(int position){
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;
        
        // Verifica a direção à esquerda
        if (position % 8 > 0 && board[position - 1] == opponent) {
            int tempPos = position - 1;
            while (tempPos % 8 > 0) { // Continua verificando na mesma linha
                tempPos--;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidCima(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção para cima
        if (position / 8 > 0 && board[position - 8] == opponent) {
            int tempPos = position - 8;
            while (tempPos / 8 > 0) { // Continua verificando na mesma coluna
                tempPos -= 8;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidBaixo(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção para baixo
        if (position / 8 < 7 && board[position + 8] == opponent) {
            int tempPos = position + 8;
            while (tempPos / 8 < 7) { // Continua verificando na mesma coluna
                tempPos += 8;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidNordeste(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção nordeste (cima à direita)
        if (position / 8 > 0 && position % 8 < 7 && board[position - 7] == opponent) {
            int tempPos = position - 7;
            while (tempPos / 8 > 0 && tempPos % 8 < 7) { // Continua verificando na diagonal
                tempPos -= 7;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidSudeste(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção sudeste (baixo à direita)
        if (position / 8 < 7 && position % 8 < 7 && board[position + 9] == opponent) {
            int tempPos = position + 9;
            while (tempPos / 8 < 7 && tempPos % 8 < 7) { // Continua verificando na diagonal
                tempPos += 9;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidSudoeste(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção sudoeste (baixo à esquerda)
        if (position / 8 < 7 && position % 8 > 0 && board[position + 7] == opponent) {
            int tempPos = position + 7;
            while (tempPos / 8 < 7 && tempPos % 8 > 0) { // Continua verificando na diagonal
                tempPos += 7;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::IsValidNoroeste(int position) {
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro

        char opponent = currentPlayer ? player2 : player1; // Jogador oponente
        char self = currentPlayer ? player1 : player2;    // Jogador atual
        bool valid = false;

        // Verifica a direção noroeste (cima à esquerda)
        if (position / 8 > 0 && position % 8 > 0 && board[position - 9] == opponent) {
            int tempPos = position - 9;
            while (tempPos / 8 > 0 && tempPos % 8 > 0) { // Continua verificando na diagonal
                tempPos -= 9;
                if (board[tempPos] == self) { // Encontrou peça do jogador atual
                    valid = true; // Jogada válida
                    break;
                } else if (board[tempPos] != opponent) { // Parar se não encontrar oponente
                    break;
                }
            }
        }

        return valid;
    }

    bool Reversi::isValidAll(int position){
        if (position < 0 || position >= 64) return false; // Verifica se está no tabuleiro
        if(IsValidEsquerda(position) ||  IsValidDireita(position) || //Verifica se a jogada é valida em qualquer direçao
        IsValidCima(position) || IsValidBaixo(position) ||
        IsValidNordeste(position) || IsValidSudeste(position) ||
        IsValidSudoeste(position) || IsValidNoroeste(position)){
            return true;
        }
        else{
            return false;
        }
    }


    void Reversi::PrintBoard(std::string jogador1, std::string jogador2){
        limpa_tela();
        int indice = 0;
        for(int i = 0; i < 8; i++){
            for(int j = 0; j < 8; j++){
                std::cout << " | "; //separadores do tabuleiro
                if (board[indice] == player1 || board[indice] == player2){
                    std::cout << (board[indice] == player1 ? "⚪" : "🔵"); //printa o simbolo do player na cor do player
                }
                else if(isValidAll(indice)){
                    std::cout << (indice <= 9 ? " " : "") << "\033[31m" << indice << "\033[0m"; //se não está ocupada mas é uma casa valida, printa o numero da casa na cor do player
                }
                else{
                    std::cout <<"  "; //se nao está ocupada e não é valida nao printa nada
                }
                indice++;
            }
            std::cout << " | "; //separadores do tabuleiro
            std::cout << std::endl;
        }
        Score(jogador1, jogador2);
    }

    void Reversi::playerMove(int position, bool isPlayer1) {
        if (position < 0 || position >= 64) return; // Verifica se está dentro do tabuleiro

        char self = isPlayer1 ? player1 : player2; // Jogador atual
        char opponent = isPlayer1 ? player2 : player1; // Adversário

        // Captura para a direita
        if (IsValidDireita(position)) {
            int tempPos = position + 1;
            while (board[tempPos] == opponent) {
                tempPos++;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos--;
            }
        }

        // Captura para a esquerda
        if (IsValidEsquerda(position)) {
            int tempPos = position - 1;
            while (board[tempPos] == opponent) { 
                tempPos--;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos++;
            }
        }

        // Captura para cima
        if (IsValidCima(position)) {
            int tempPos = position - 8;
            while (board[tempPos] == opponent) {
                tempPos -= 8;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos += 8;
            }
        }

        // Captura para baixo
        if (IsValidBaixo(position)) {
            int tempPos = position + 8;
            while (board[tempPos] == opponent) {
                tempPos += 8;
            }
            while(tempPos != position){
            if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos -= 8;
            }
        }

        // Captura para nordeste
        if (IsValidNordeste(position)) {
            int tempPos = position - 7;
            while (board[tempPos] == opponent) {
                tempPos -= 7;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos += 7;
            }
        }

        // Captura para sudeste
        if (IsValidSudeste(position)) {
            int tempPos = position + 9;
            while (board[tempPos] == opponent) {
                tempPos += 9;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos -= 9;
            }
        }

        // Captura para sudoeste
        if (IsValidSudoeste(position)) {
            int tempPos = position + 7;
            while (board[tempPos] == opponent) {
                tempPos += 7;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos -= 7;
            }
        }

        // Captura para noroeste
        if (IsValidNoroeste(position)) {
            int tempPos = position - 9;
            while (board[tempPos] == opponent) {
                tempPos -= 9;
            }
            while(tempPos != position){
                if(board[tempPos] != self){
                    board[tempPos] = self; //Vai preenchendo as casas com o simbolo do player
                    AnimacaoCaptura();
                }
                tempPos += 9;
            }
        }

        // Marca a posição atual como do jogador atual
        board[position] = self;
    }



    void Reversi::Inicio(){
        board[27] = player1; //Preenche as casas iniciais no padrão do Reversi
        board[36] = player1;
        board[28] = player2;
        board[35] = player2;
    }

    bool Reversi::CanIPlay(){ //Verifica se existe alguma jogada válida para o player
        bool ans = false;
        for(int i = 0; i < 64; i++){
            if(isValidAll(i) && board[i] == ' '){
                ans = true;
                break;
            }
        }
        return ans;
    }

    bool Reversi::CheckTie(){ //Verifica se o jogo terminou (nenhum dos jogadores tem jogada válida)
        bool test1, test2;

        test1 = CanIPlay();
        CheckGameStatus();
        test2 = CanIPlay();
        if(test1 || test2){
            CheckGameStatus();
            return false;
        }
        else{
            CheckGameStatus();
            return true;
        }
    }

    void Reversi::Score(std::string jogador1, std::string jogador2){ //Conta o score e exibe na tela
        int score1 = 0, score2 = 0;;
        for(int i = 0; i < 64; i++){
            if(board[i] == 'X'){
                score1++;
            }
        }

        for(int i = 0; i < 64; i++){
            if(board[i] == 'O'){
                score2++;
            }
        }
        std::cout << "Score: " << jogador1 << " (" <<score1 << ") / " << jogador2 << " (" << score2 << ")" << std::endl;
    }

    int Reversi::CheckWin(std::string jogador1, std::string jogador2){ //Conta quem tem mais símbolos no tabuleiro para a vitória
        int X = 0, O = 0;
        for(int i = 0; i < 64; i++){
            if(board[i] == 'X'){
                X++;
            }

            else if(board[i] == 'O'){
                O++;
            }
        }
        PrintBoard(jogador1, jogador2);

        if(X != O){
            std::cout << "PARABENS!!! " << (X > O ? jogador1 : jogador2) << " voce venceu" << std::endl;
            sleep(2);
            return X > O;
        }
        else{
            std::cout << "O jogo empatou!" << std::endl;
            return -1;
        }
    }

    void Reversi::CheckGameStatus(){ //Troca o player, passa a vez
        currentPlayer = !currentPlayer;
    }

    void Reversi::AnimacaoCaptura(){
        limpa_tela();
        int indice = 0;
        for(int i = 0; i < 8; i++){
            for(int j = 0; j < 8; j++){
                std::cout << " | "; //separadores do tabuleiro
                if (board[indice] == player1 || board[indice] == player2){
                    std::cout << (board[indice] == player1 ? "⚪" : "🔵"); //printa o simbolo do player na cor do playr
                }
                else{
                    std::cout <<"  "; //se nao está ocupada e não é valida nao printa nada
                }
                indice++;
            }
            std::cout << " | "; //separadores do tabuleiro
            std::cout << std::endl;
        }
        sleep(0.5);
    }

    //Implementação de um jogo de Reversi
    void Reversi::JogarReversi(std::string jogador1, std::string jogador2, cadastro &meucadastro, Reversi &Reversi){
        int position;
        Inicio();
        while(position != -1){

            //Se o jogador tem jogadas válidas ele vai jogar
            if(CanIPlay()){
                PrintBoard(jogador1, jogador2);
                std::cout << (currentPlayer ? jogador1 : jogador2) << ", escolha entre as casas válidas (-1 finaliza o jogo): " << std::endl;

                std::cin >> position;

                
            //evita que position receba char por exemplo
            if (validacao_entrada()) {
                continue; // Volta para o início do loop
            }

                //Se a jogada é válida, faz a jogada e passa a vez
                if(isValidAll(position)){
                    playerMove(position, currentPlayer);
                    AnimacaoCaptura();
                    CheckGameStatus();
                }
                //Se a jogada não é valida exibe mensagem de erro e o mesmo jogador tenta jogar novamente
                else if (position != -1){
                    std::cout << "Jogada invalida, siga os numeros no tabuleiro" << std::endl;
                    sleep(2);
                }
            }

            //Se o jogador nao tem jogadas válidas, passa a vez
            else{
                CheckGameStatus();
            }

            //Checa se o jogo acabou após cada rodada
            if(CheckTie()){
                break;
            }
        }


        //Confere quem venceu e exibe na tela, além de atualizar as estatísticas
        if(position != -1){
            int resultado = CheckWin(jogador1, jogador2);
            if(resultado == 1){ 
                meucadastro.SetVD(jogador1,jogador2,3);
            }
            else if (resultado == 0){
                meucadastro.SetVD(jogador2,jogador1,3);
            }
            else if (resultado == -1){
                std::cout << "nenhuma vitoria registrada" << std::endl;
            }
        }
    }
}