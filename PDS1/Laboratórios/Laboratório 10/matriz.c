#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void printamatriz(int **matriz,int m, int n)
{
    for(int i=0;i<m;i++)
    {
      for(int j=0;j<n;j++)
        printf("%d ",matriz[i][j]);
      printf("\n");
    }

}
void liberamatriz(int **matriz,int m)
{
    for(int i=0;i<m;i++)
        free(matriz[i]);
    free(matriz);
}
int main()
{
    int **matriz,i,j,m,n;
    scanf("%d %d",&m,&n);
    matriz=(int **)malloc(m*sizeof(int*));
    for(i=0;i<m;i++)
    {
        matriz[i]=(int *)malloc(n*sizeof(int));
        for(j=0;j<n;j++)
           scanf("%d",&matriz[i][j]);
    }
    printamatriz(matriz,m,n);
    liberamatriz(matriz,m);
}
