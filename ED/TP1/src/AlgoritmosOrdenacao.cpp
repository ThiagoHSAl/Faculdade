  #include "AlgoritmosOrdenacao.hpp"
  #include "OrdenadorUniversal.hpp"
  #include "AnaliseExperimental.hpp"
  #include "itemT.hpp"
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

  item_t mediana(item_t a, item_t b, item_t c) {
      if ((a <= b) && (b <= c)) return b;  // a b c
      if ((a <= c) && (c <= b)) return c;  // a c b
      if ((b <= a) && (a <= c)) return a;  // b a c
      if ((b <= c) && (c <= a)) return c;  // b c a
      if ((c <= a) && (a <= b)) return a;  // c a b
      return b;                            // c b a
  }

  void insercao(item_t* v, int l, int r, estatisticas *s) {
      inccalls(s, 1); 
      int i,j;
      for (i = l+1; i <= r; i++) {
          item_t aux = v[i];
          incmove(s, 1);
          int j = i - 1;
          inccmp(s, 1);
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

  void particao(item_t * A, int l, int r, int *i, int *j, estatisticas *s) {
    int m = l + (r - l) / 2;
    item_t pivot = mediana(A[l], A[m], A[r]);
    
    *i = l;
    *j = r;
    
    do {
        while (A[*i] < pivot) {
            inccmp(s, 1);
            (*i)++;
        }
        inccmp(s, 1);
        
        while (A[*j] > pivot) {
            inccmp(s, 1);
            (*j)--;
        }
        inccmp(s, 1);
        
        if (*i <= *j) {
            swap(A[*i], A[*j], s);
            (*i)++;
            (*j)--;
        }
    } while (*i <= *j);
  }

  void quickSort(item_t *A, int l, int r, int menorTamanhoParticao, estatisticas *s) {
    inccalls(s, 1); 
      
    int i, j;
    particao(A, l, r, &i, &j, s);
    inccalls(s, 1);
    
    if (l < j){
      if((j - l + 1) <= menorTamanhoParticao){
        insercao(A, l, j, s);
      }
      else{
        quickSort(A, l, j, menorTamanhoParticao, s);
      }
    }
    if (i < r){
      if((r - i + 1) <= menorTamanhoParticao){
        insercao(A, i, r, s);
      }
      else{
        quickSort(A, i, r, menorTamanhoParticao, s);
      }
    }
  }


  int embaralharVetor(item_t *vetor, int tamanho, int numTrocas){
      int indice1 = 0, indice2 = 0;
      item_t temp;
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

  int contaQuebras(item_t* vetor, int inicio, int final){
    int quantidadeQuebras = 0;
    for(int i = inicio; i < final - 1; i++){
        if(vetor[i] > vetor[i + 1]){
            quantidadeQuebras++;
        }
    }
    return quantidadeQuebras;
}

