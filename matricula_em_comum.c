#include<stdio.h>
#include<stdlib.h>

int main()
{
    int aeds,matricula_calculo[100],matricula_aeds[100], calculo,i,j;
    printf("digite a quantidade de alunos matriculados em AEDS\n");
    scanf("%d",&aeds);
    printf("digite o numero de matricula dos alunos de AEDS\n");
    for(i=0;i<aeds;i++)
    {
        scanf("%d",&matricula_aeds[i]);
    }
    printf("digite a quantidade de alunos matriculados em Caulculo \n");
    scanf("%d",&calculo);
    printf("digite o numero de matricula dos alunos de Calculo\n");
    for(i=0;i<calculo;i++)
    {
        scanf("%d",&matricula_calculo[i]);
    }
    for(i=0;i<aeds;i++)
    {
        for(j=0;j<calculo;j++)
        {
            if(matricula_aeds[i]==matricula_calculo[j])
            printf("%d\n",matricula_calculo[j]);
        }
    }
}