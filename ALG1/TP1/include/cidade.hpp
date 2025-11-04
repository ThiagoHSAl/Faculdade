#ifndef CIDADE_HPP
#define CIDADE_HPP

#include <string>
#include <vector>
#include <list>
#include <set>

#define LL long long int

class Rua {
public:
    Rua(LL indice, LL comprimento, LL destino) : indice(indice), comprimento(comprimento), destino(destino) {}
    Rua(LL comprimento, LL destino) : indice(-1), comprimento(comprimento), destino(destino) {}

    bool estaEmUmCaminhoMinimo(LL distDaOrigemAU, LL distDeVAoDestino, LL menorDistanciaTotal) const;
    bool eCritica(LL caminhosMinimosDaOrigemAU, LL caminhosMinimosDeVAoDestino, LL numeroTotalDeCaminhosMinimos) const;
    bool operator>(const Rua& outra) const {
        return this->comprimento > outra.comprimento;
    }
    LL getDestino() const;
    LL getComprimento() const;
    LL getIndice() const;

private:
    LL indice;
    LL comprimento;
    LL destino;
};


class Cidade{
public:
    Cidade(LL numBairros);
    void adicionarRua(LL indice, LL origem, LL destino, LL distancia);

    // Versão 1: Apenas calcula as distâncias
    void dijkstra(LL origem, std::vector<LL>& distancias) const;
    // Versão 2: Calcula distâncias E número de caminhos minimos
    void dijkstra(LL origem, std::vector<LL>& distancias, std::vector<LL>& numCaminhosMinimos) const;
   
    LL buscarMenorCaminho(LL origem, LL destino);
    std::set<LL> encontrarRuasEmUmCaminhoMinimo(LL origem, LL destino);
    std::set<LL> encontrarRuasCriticas(LL origem, LL destino);
private:
    std::vector<std::list<Rua>> grafoCidade;
    //Conta ou não os caminhos mínimos dependendo de qual dos 2 dijkstras a chama
    void dijkstra_core(LL origem, std::vector<LL>& distancias, std::vector<LL>* numCaminhosMinimos) const;
};


#endif // CIDADE_HPP