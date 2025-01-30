#ifndef JOGADOR_HPP
#define JOGADOR_HPP
#include<iostream>
#include<string>

class jogador{
    private:
    std::string _nome, _apelido;
    int vitorias[3],derrotas[3];

    public:
    jogador(std::string nome, std::string apelido);
    jogador(std::string nome, std::string apelido, int vitorias[], int derrotas[]);
    std::string GetNome() const;
    std::string GetApelido() const;
    std::string GetEstatisticas() const;
    int GetVitoria(int jogo) const;
    void SetNome(std::string nome);
    void SetApelido(std::string novoapelido);
    void SetEstatistica(int V_D);
    void Imprime() const;
};
#endif