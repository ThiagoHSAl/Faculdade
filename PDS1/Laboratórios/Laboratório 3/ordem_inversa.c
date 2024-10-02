#include<stdio.h>
#include<stdlib.h>

int main()
{
    int vetor[10], vetor2[10],i,j=9;
    for(i=0;i<=9;i++)
    {
        scanf("%d",&vetor[i]);
        vetor2[j]=vetor[i];
        j--;
    }
    for(i=0;i<=9;i++)
    printf("%d\n",vetor2[i]);
}