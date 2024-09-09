#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct registro{
    char nome[50];
    unsigned int idade;
    float salario;
};
int main()
{
    struct registro r[4];
    char entrada[50],entrada2[50],nome[50];
    int i=0,j,ausente;
    do
    {
    strcpy(entrada2,"a");   
    scanf("%s",entrada2);
    if (strcmp("inserir",entrada2)==0)
    {
       if(i<=3)
       {
       scanf("%s %d %f",r[i].nome,&r[i].idade,&r[i].salario);
       printf("Registro %s %d %.2f inserido\n", r[i].nome,r[i].idade,r[i].salario);
       i++;
       }
       else{
           printf("Espaco insuficiente\n");
       }
    }
    else if (strcmp("mostrar",entrada2)==0)
    {
       ausente=1;
       scanf("%s",nome);
       for(j=0;j<4;j++)
       {
           if(strcmp(r[j].nome,nome)==0)
           {
               printf("Registro %s %d %.2f\n",r[j].nome,r[j].idade,r[j].salario);
               ausente=0;
           }
       }
       if(ausente==1)
       {
       printf("Registro ausente\n");
       }
    }
    }while(fgets(entrada,50,stdin) != NULL);
}
