#include<stdio.h>
#include<stdlib.h>

int main()
{
    int linhas, colunas, i, j, maior;
    printf("digite o numero de linhas da matriz\n");
    scanf("%d",&linhas);
    printf("digite o numero de colunas da matriz\n");
    scanf("%d",&colunas);
    int matriz[linhas][colunas];
    printf("digite os valores matriz\n");
    for(i=0;i<linhas;i++)
    {
        for(j=0;j<colunas;j++)
        {
          scanf("%d",&matriz[i][j]);  
        }
    }
    maior=matriz[0][0];
    for(i=0;i<linhas;i++)
    {
        for(j=0;j<colunas;j++)
        {
          if(maior<matriz[i][j])
          maior=matriz[i][j];
        }
    }
    printf("%d", maior);
}
