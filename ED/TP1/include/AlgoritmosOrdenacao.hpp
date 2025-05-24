#ifndef ALGORITMOSORDENACAO_HPP
#define ALGORITMOSORDENACAO_HPP

#include "estatisticas.hpp"
#include "itemT.hpp"

void resetcounter(estatisticas * s);

void inccmp(estatisticas * s, int num);

void incmove(estatisticas * s, int num);

void inccalls(estatisticas * s, int num);

int mediana(int a, int b, int c);

void swap(int *xp, int *yp, estatisticas *s);

void insercao(item_t* v, int l, int r, estatisticas *s);

void particao(item_t* A, int l, int r, int *i, int *j, estatisticas *s);

void quickSort(item_t* A, int l, int r, int menorTamanhoParticao, estatisticas *s);

int embaralharVetor(item_t* vetor, int tamanho, int numTrocas);

int contaQuebras(item_t* vetor, int inicio, int final);

inline void swap(item_t& a, item_t& b, estatisticas *s) {
    item_t temp = a;
    a = b;
    b = temp;
    incmove(s,3);
}

#endif