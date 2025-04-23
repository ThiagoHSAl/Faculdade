#include "ListaAdjacencia.hpp"
#include "TipoCelula.hpp"
#include <iostream>

ListaAdjacencia::ListaAdjacencia(int item){
    primeiro = new TipoCelula(item);
    ultimo = primeiro;
    tamanho = 1;
}

ListaAdjacencia::~ListaAdjacencia(){
    Limpa();
    delete primeiro;
}

void ListaAdjacencia::Insere(int item){
    TipoCelula *nova;

    nova = new TipoCelula();
    nova->item = item;
    ultimo->proximo = nova;
    ultimo = nova;
    tamanho++;
}

void ListaAdjacencia::Imprime(){
    TipoCelula *impressao;

    impressao = primeiro->proximo;
    while(impressao != nullptr){
        std::cout << impressao->item << " ";
        impressao = impressao -> proximo;
    }
    std::cout<<std::endl;
}

void ListaAdjacencia::Limpa(){
    TipoCelula *limpeza;

    limpeza = primeiro->proximo;
    while(limpeza != nullptr){
        primeiro->proximo = limpeza->proximo;
        delete limpeza;
        limpeza = primeiro->proximo;
    }
    ultimo = primeiro;
    tamanho = 0;
}

int ListaAdjacencia::GetTamanho(){
    return tamanho-1;
}


