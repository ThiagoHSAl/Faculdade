#ifndef CADASTRO_HPP
#define CADASTRO_HPP
#include "jogador.hpp"
#include <iostream>
#include <string>
#include <vector>

class cadastro{
    private:
    std::vector<jogador> _MeuCadastro;

    public:
    cadastro();
    ~cadastro();
    void CadastraJogador(std::string nome, std::string apelido);
    void DeletaJogador(std::string apelido);
    void EditaJogador(std::string apelido, std::string novoapelido);
    int VerificaApelido(std::string apelido);
    void SetVD (std::string playerV, std::string playerD, int game);
    void Imprime();
    void Ranking();
    void ExibeApelidos();
    bool login(std::string &jogador1, std::string &jogador2, cadastro &meucadastro);
};
    

#endif
