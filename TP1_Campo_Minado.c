#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main()
{
    int quantidade_jogos,tamanho_tabuleiro,quantidade_jogadas,i,j,k,jogadai,jogadaj,perdeu,faltou,bomba;
    char tabuleiro[100][100],leitura[201];//inputs de 100 caracteres, 100 espaços e 1 caracter nulo
    scanf("%d",&quantidade_jogos);
  while(quantidade_jogos>0)
  {
    perdeu=0; // reseta o status de perdeu
    faltou=0; // reseta o status de faltou terminar
    scanf("%d",&tamanho_tabuleiro);
    getchar();//limpa o buffer do teclado
    for (i=0;i<tamanho_tabuleiro;i++)
    {
        fgets(leitura,201,stdin); // recebe o input do tabuleiro em formato string
        leitura[strcspn(leitura, "\n")] = '\0'; // retira o caractere \n da string
        j=0; // reinicia o índice da coluna
        k=0; // reinicia o indice do array leitura
        while(leitura[k] != '\0') // percorre toda a string
        {
            if(leitura[k]=='x' || leitura[k]=='b' ) // desconsidera os espaços e utiliza apenas os caracteres x e b
            {
                tabuleiro[i][j]=leitura[k]; // atribui ao tabuleiro a string digitada no teclado, sem os espaços
                j++;
            }
            k++;
        }
    }   
    scanf("%d",&quantidade_jogadas);
    for(i=0;i<quantidade_jogadas;i++)
    {
        bomba=0;// reseta o status de bomba na casa
        scanf("%d %d",&jogadai,&jogadaj);
        if(tabuleiro[jogadai][jogadaj]=='b')// se a jogada for em cima de uma bomba o jogador perde
            perdeu=1;
        if(tabuleiro[jogadai][jogadaj]=='x'&& perdeu!=1) //se a jogada for em cima de um x, será verificado se existe boma adjacente
        {
            for(j=jogadai-1;j<=jogadai+1;j++)
            for(k=jogadaj-1;k<=jogadaj+1;k++)
            {
                if(tabuleiro[j][k]=='b')
                bomba=1;
            }
            if(bomba==1)
            tabuleiro[jogadai][jogadaj]='l'; //se houver bomba adjacente, revela apenas a casa que o jogador jogou
            if(bomba==0)
            for(j=jogadai-1;j<=jogadai+1;j++)
            for(k=jogadaj-1;k<=jogadaj+1;k++)
            {
                tabuleiro[j][k]='l';//se não houver bomba adjacente, revela todas as casas adjacentes e a casa jogada
            }
        }
    }
    if(perdeu==1)
        printf("PERDEU\n");
        if(perdeu!=1)
        {
          for(i=0;i<tamanho_tabuleiro;i++)
            for(j=0;j<tamanho_tabuleiro;j++)
            {
              if(tabuleiro[i][j]=='x') // se restar alguma casa no tabuleiro que não seja revelada ou bomba, faltou terminar
              faltou=1;
            }
       if(faltou==1)
          printf("FALTOU TERMINAR\n");
       if(perdeu!=1 && faltou!=1) //se nao faltou terminar e nao perdeu, então ganhou
       {
          printf("GANHOU\n");
       }
       }
   quantidade_jogos--;
  }
}



