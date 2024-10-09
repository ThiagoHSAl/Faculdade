#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <cctype>
#include <bits/stdc++.h>

using namespace std;

vector<string> palavras;
string letras_erradas,jogo="*****";//Variáveis declaradas globalmente, pois são usadas constantemente pela função wordle

bool wordle(string chute, string palavra){ //Função que compara o chute do jogador com a palavra certa
  int i;
  for(i=0;i<5;i++){
    if(palavra.find(chute[i])!=string::npos){
      if(palavra[i]==chute[i]){//Se o carctere existe na palavra e está na posição correta
        jogo[i]=chute[i];//A variável jogo é a referencia do jogador de quais caracteres estão certos e se estão na posição correta
      }
       else
       jogo[i]=tolower(chute[i]);//Se o caractere existe na palavra, mas em outra posição
    }
    else{
      if(letras_erradas.find(chute[i])==string::npos)//Importante para não adicionar a mesma letra errada várias vezes na lista de letras erradas
      letras_erradas.push_back(chute[i]);
    }
  }
    cout<<jogo<<" ("<<letras_erradas<<")"<<endl;
    for(i=0;i<5;i++){
        if(islower(jogo[i]))//Volta as letras certas na posição errada para o caractere * para que não atrapalhe as proximas impressoes
            jogo[i]='*';
    }
  return chute==palavra;
}
int main()
{
    int n;
   string palavra;
   ifstream arquivo("palavras.txt");
   if(arquivo.is_open()){
   arquivo>>n; //utilizado apenas para consumir o primeiro int do arquivo, ja que aqui foi utilizado um laço while que leria quantas palavras o arquivo tivesse
    while(getline(arquivo>>ws,palavra))//utilizado o whitespace manipulator para evitar ler a quebra de linha entre o int e lista de palavras
     palavras.push_back(palavra);
    arquivo.close();
   }
   else{
   return 1;
   }
   string chute;
   int chave,i;
   cin>>chave;
   chave--; //Serve para manter a chave 0 based, para refletir corretamente o indice no vetor de strings
   palavra=palavras[chave];
   for(i=0;i<5;i++){
     cin>>chute;
     if(wordle(chute,palavra)){ //a função wordle retorna true se o chute estiver correto, por isso o programa pode ser encerrado
       cout<<"GANHOU!"<<endl;
       return 0;
     }
   }
    cout<<"PERDEU! "<<palavra<<endl; //caso o laço de 5 tentativas se esgote, significa que o jogador perdeu
    return 0;
}
