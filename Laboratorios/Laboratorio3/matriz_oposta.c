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
    for(i=0;i<linhas;i++)
    {
        for(j=0;j<colunas;j++)
        {
          matriz[i][j]=-matriz[i][j];
          printf("%d ",matriz[i][j]);
        }
        printf("\n");
    }
}
