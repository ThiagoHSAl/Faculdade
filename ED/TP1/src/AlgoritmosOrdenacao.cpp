  #include "AlgoritmosOrdenacao.hpp"
  #include "OrdenadorUniversal.hpp"
  #include <stdlib.h>
  #include <algorithm>
  #include <math.h>

  void resetcounter(estatisticas * s){
    s->cmp = 0;
    s->move = 0;
    s->calls = 0;
  }

  void inccmp(estatisticas * s, int num){
    s->cmp += num;
  }

  void incmove(estatisticas * s, int num){
    s->move += num;
  }

  void inccalls(estatisticas * s, int num){
    s->calls += num;
  }

  int mediana(int a, int b, int c) {
      if ((a <= b) && (b <= c)) return b;  // a b c
      if ((a <= c) && (c <= b)) return c;  // a c b
      if ((b <= a) && (a <= c)) return a;  // b a c
      if ((b <= c) && (c <= a)) return c;  // b c a
      if ((c <= a) && (a <= b)) return a;  // c a b
      return b;                            // c b a
  }

  void swap(int *xp, int *yp, estatisticas *s){
      int temp = *xp;
      *xp = *yp;
      *yp = temp;
      incmove(s,3);
  }

  void insercao(int* v, int l, int r, estatisticas *s) {
      inccalls(s, 1);  // conta chamada da função
      int i,j,aux;
      for (i = l+1; i <= r; i++) {
          aux = v[i];
          incmove(s, 1);
          int j = i - 1;
          inccmp(s, 1);
          // Contabiliza ambas as condições do while separadamente
          while ((j >= l) && (aux < v[j])){
              inccmp(s, 1);
              v[j + 1] = v[j];
              incmove(s, 1);
              j--;
          }
          v[j + 1] = aux;
          incmove(s, 1);
      }
  }

  void particao(int * A, int l, int r, int *i, int *j, estatisticas *s) {
      // Find mediana of first, middle and last elements
      int m = l + (r - l) / 2;
      int pivot = mediana(A[l], A[m], A[r]);
      
      *i = l;
      *j = r;
      
      do {
          while (A[*i] < pivot) {
              inccmp(s, 1);
              (*i)++;
          }
          inccmp(s, 1); // Count the last comparison that failed
          
          while (A[*j] > pivot) {
              inccmp(s, 1);
              (*j)--;
          }
          inccmp(s, 1); // Count the last comparison that failed
          
          if (*i <= *j) {
              swap(&A[*i], &A[*j], s);
              (*i)++;
              (*j)--;
          }
      } while (*i <= *j);
  }

  void quickSort(int *A, int l, int r, int menorTamanhoParticao, int limiarQuebras, estatisticas *s) {
    inccalls(s, 1); // Conta esta chamada
      
    int i, j;
    particao(A, l, r, &i, &j, s);
    inccalls(s, 1); // Conta esta chamada
    // Chamadas recursivas
    if (l < j){
      if((j - l + 1) <= menorTamanhoParticao || contaQuebras(A,l,j) < limiarQuebras){
        insercao(A, l, j, s);
      }
      else{
        quickSort(A, l, j, menorTamanhoParticao, limiarQuebras, s);
      }
    }
    if (i < r){
      if((r - i + 1) <= menorTamanhoParticao || contaQuebras(A,i,r) < limiarQuebras){
        insercao(A, i, r, s);
      }
      else{
        quickSort(A, i, r, menorTamanhoParticao, limiarQuebras, s);
      }
    }
  }


  int embaralharVetor(int *vetor, int tamanho, int numTrocas){
      int indice1 = 0, indice2 = 0, temp;

      for (int i = 0; i < numTrocas; i++) {
          // Gera dois índices distintos no intervalo [0..tamanho-1]
          while (indice1 == indice2) {
              indice1 = (int)(drand48() * tamanho);
              indice2 = (int)(drand48() * tamanho);
          }

          // Realiza a troca entre os elementos dos índices sorteados
          temp = vetor[indice1];
          vetor[indice1] = vetor[indice2];
          vetor[indice2] = temp;

          // Reinicia os índices para a próxima iteração
          indice1 = indice2 = 0;
      }
      return 0;
  }

