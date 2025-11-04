#include "cidade.hpp"
#include <iostream>
#include <stdexcept>

int main() {

    try{
        LL numBairros, numRuas;
        std::cin >> numBairros >> numRuas;
        Cidade cidade(numBairros);

        if(numRuas < 0){
            throw std::invalid_argument("Erro: Número de ruas não pode ser negativo.");
        }

        //Recebe as ruas no padrão do enunciado e adiciona ao grafo
        for (LL i = 1; i <= numRuas; ++i) {
            LL origem, destino, distancia;
            std::cin >> origem >> destino >> distancia;
            cidade.adicionarRua(i, origem-1, destino-1, distancia);
        }   //subtrai 1 pois a entrada é 1-indexada e o vetor é 0-indexado

        LL menorCaminho;

        //No problema, a origem é sempre zero e o destino é sempre o último vértice
        menorCaminho = cidade.buscarMenorCaminho(0, numBairros-1);
        std::cout << "Parte 1: " << menorCaminho << std::endl;

        std::set<LL> ruasEmUmCaminhoMinimo;
        ruasEmUmCaminhoMinimo = cidade.encontrarRuasEmUmCaminhoMinimo(0, numBairros-1);

        std::cout << "Parte 2: ";
        if (ruasEmUmCaminhoMinimo.empty()) {
            std::cout << "-1";
        }
        else {
            for (LL indice : ruasEmUmCaminhoMinimo) {
            std::cout << indice << " ";
            }
        }
        std::cout << std::endl;

        std::set<LL> ruasCriticas;
        ruasCriticas = cidade.encontrarRuasCriticas(0, numBairros-1);

        std::cout << "Parte 3: ";
        if (ruasCriticas.empty()) {
            std::cout << "-1";
        }
        else {
            for (LL indice : ruasCriticas) {
                std::cout << indice << " ";
            }
        }
        std::cout << std::endl;
    }

    catch(const std::overflow_error& e){
        std::cerr << e.what() << std::endl;
        return 1;
    }

    catch(const std::invalid_argument& e){
        std::cerr << e.what() << std::endl;
        return 1;
    }

    catch(const std::out_of_range& e){
        std::cerr << e.what() << std::endl;
        return 1;
    }

    catch(const std::runtime_error& e){
        std::cerr << e.what() << std::endl;
        return 1;
    }

    catch(...){
        std::cerr << "Erro desconhecido." << std::endl;
        return 1;
    }

    return 0;
}