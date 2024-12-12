#include <iostream>
#include<bits/stdc++.h>
 
using namespace std;
 

 // 0) Crie uma função que receba três variveis inteiras como parâmetro, da seguinte forma:
//    - A primeira deve ser passada por valor
//    - A segunda deve ser passada por referência 
//    - A terceira deve ser passada "por referência" usando apontadores (passagem "por referência" disponível em C)
//    A função deverá somar 1 ao valor de cada uma das 3 variáveis e retornar.

int soma3(int a, int &b, int *c){
  a++;
  b++;
  (*c)++;
  return a;
}

int main(){

  int a; cin>>a;  // 1) Declare uma variável do tipo inteiro e preencha com o valor informado na entrada
    
    
  int *b=nullptr;  // 2) Declare um ponteiro para inteiros e inicialize com valor nulo
    

  int *vec,i,tam; 
  cin>>tam; 
  vec=new int[tam]; 
  for(i=0;i<tam;i++)cin>>vec[i]; // 3) Declare um vetor de inteiros com tamanho informado na entrada e preencha com dados lidos da entrada
    

  cout<<&a<<endl; // 4) Imprima o ENDEREÇO da variável declarada em (1)
    

  cout<<a<<endl; // 5) Imprima o VALOR da variável declarada em (1)
    

  cout<<&b<<endl; // 6) Imprima o ENDEREÇO da variável declarada em (2)
    
    
  cout<<b<<endl; // 7) Imprima o VALOR da variável declarada em (2)
    

  cout<<&vec<<endl;  // 8) Imprima o ENDEREÇO da variável declarada em (3)
    

  cout<<&vec[0]<<endl;  // 9) Imprima o ENDEREÇO da primeira posição da variável declarada em (3)
    

  cout<<vec[0]<<endl; // 10) Imprima o VALOR da primeira posição da variável declarada em (3)
    

  b=&a;  // 11) Atribua o ENDEREÇO da variável declarada em (1) à variável declarada em (2)
    

  cout<<b<<endl;  // 12) Imprima o VALOR da variável declarada em (2)
    

  cout<<*b<<endl;  // 13) Imprima o VALOR guardado no ENDEREÇO apontado por (2)
    

  *b=5;  // 14) Coloque o VALOR '5' no ENDEREÇO apontado por (2)
    

  cout<<a<<endl;  // 15) Imprima o VALOR da variável declarada em (1)
    

  *b=vec[0];  // 16) Atribua o VALOR da variável (3) à variável declarada em (2)
    

  cout<<b<<endl;  // 17) Imprima o VALOR da variável declarada em (2)
    

  cout<<*b<<endl;  // 18) Imprima o VALOR guardado no ENDEREÇO apontado por (2)
    

  b=vec;  // 19) Atribua o ENDEREÇO da primeira posição de (3) à variável declarada em (2)
    

  if(b==vec) 
  cout<<"S"<<endl; 
  else 
  cout<<"N"<<endl;  // 20) Compare o valor variáveis (2) e (3), imprimindo 'S' se forem iguais e 'N' se forem diferentes


  cout<<b<<endl;  // 21) Imprima o VALOR da variável declarada em (2)
    

  cout<<*b<<endl;  // 22) Imprima o VALOR guardado no ENDEREÇO apontado por (2)
    

  for(i=0;i<tam;i++) 
  b[i]*=10;  // 23) Multiplique todos os valores do vetor declarado em (3) por '10', porém manipulando apenas a variável (2)
    

  for(i=0;i<tam-1;i++) 
  cout<<vec[i]<<" "; 
  cout<<vec[tam-1]<<endl; // 24) Imprima os elementos de (3) a partir variável do vetor utilizando a notação [] (colchetes)
    

  for(i=0;i<tam-1;i++) 
  cout<<*(vec+i)<<" "; 
  cout<<*(vec+i)<<endl;  // 25) Imprima os elementos de (3) a partir variável do vetor utilizando a notação ponteiro/deslocamento
    // Ou seja, você NÃO deve efetivamente alterar o valor do ponteiro inicial de (3)
    

  for(i=0;i<tam-1;i++) 
  cout<<*(b+i)<<" "; 
  cout<<*(b+i)<<endl;  // 26) Imprima os elementos de (3) utilizando a variável (2) e a notação ponteiro/deslocamento
    // Ou seja, você NÃO deve efetivamente alterar o valor do ponteiro inicial de (2)
    

  b=&vec[tam-1];  // 27) Atribua o ENDEREÇO da última posição de (3) à variável declarada em (2)
    

  cout<<b<<endl;  // 28) Imprima o VALOR da variável declarada em (2)
    

  cout<<*b<<endl;  // 29) Imprima o VALOR guardado no ENDEREÇO apontado por (2)
    

  int **p=&b;  // 30) Declare um ponteiro para ponteiro e o inicialize com o ENDEREÇO da variável (2)
    

  cout<<p<<endl;  // 31) Imprima o VALOR da variável declarada em (30)
    

  cout<<&p<<endl;  // 32) Imprima o ENDEREÇO da variável declarada em (30)
    

  cout<<*p<<endl;  // 33) Imprima o VALOR guardado no ENDEREÇO apontado por (30)
    

  cout<<**p<<endl;  // 34) Imprima o VALOR guardado no ENDEREÇO do ponteiro apontado por (30)
    

  int x,y,z; 
  cin>>x>>y>>z;  // 35) Crie 3 variáveis interiras e leia o valor delas da entrada


  i=soma3(x,y,&z);  // 36) Chame a função criada em (0) passando as 3 variáveis criadas em (35) como parâmetro.

    
  cout<<x<<" "<<y<<" "<<z<<endl;  // 37) Imprima o valor das 3 variáveis criadas em (35)
    
    return 0;
}