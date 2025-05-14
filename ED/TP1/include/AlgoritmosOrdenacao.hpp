#ifndef ALGORITMOSORDENACAO_HPP
#define ALGORITMOSORDENACAO_HPP
#include "OrdenadorUniversal.hpp"

void resetcounter(estatisticas * s);

void inccmp(estatisticas * s, int num);

void incmove(estatisticas * s, int num);

void inccalls(estatisticas * s, int num);

int mediana(int a, int b, int c);
;
void swap(int *xp, int *yp, estatisticas *s);

void insercao(int* v, int l, int r, estatisticas *s);

void particao(int* A, int l, int r, int *i, int *j, estatisticas *s);

void quickSort(int* A, int l, int r, int menorTamanhoParticao, int limiarQuebras, estatisticas *s);

int embaralharVetor(int *vetor, int tamanho, int numTrocas);

#endif