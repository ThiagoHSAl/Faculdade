#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct endereco{
    char rua[50];
    unsigned int numero;
    char estado[50];
};

struct registro{
    char nome[50];
    unsigned int idade;
    float salario;
    struct endereco ender;
};
int main()
{
    struct registro r[5];
    char entrada[50],entrada2[50],nome[50];
    int i=0,j,ausente;
    do
    {
    strcpy(entrada2,"a");   
    scanf("%s",entrada2);
    if (strcmp("inserir",entrada2)==0)
    {
       if(i<=4)
       {
       scanf("%s %d %f %s %d %s",r[i].nome,&r[i].idade,&r[i].salario,r[i].ender.rua,&r[i].ender.numero,r[i].ender.estado);
       printf("Registro %s %d %.2f %s %d %s inserido\n", r[i].nome,r[i].idade,r[i].salario,r[i].ender.rua,r[i].ender.numero,r[i].ender.estado);
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
       for(j=0;j<5;j++)
       {
           if(strcmp(r[j].nome,nome)==0)
           {
               printf("Registro %s %d %.2f %s %d %s\n", r[j].nome,r[j].idade,r[j].salario,r[j].ender.rua,r[j].ender.numero,r[j].ender.estado);
               ausente=0;
           }
       }
       if(ausente==1)
       {
       printf("Registro ausente\n");
       }
    }
    else if (strcmp("alterar",entrada2)==0)
    {
        ausente=1;
        scanf("%s",nome);
        for(j=0;j<5;j++)
       {
           if(strcmp(r[j].nome,nome)==0)
           {
           strcpy(r[j].nome,nome);
           scanf("%d %f %s %d %s",&r[j].idade,&r[j].salario,r[j].ender.rua,&r[j].ender.numero,r[j].ender.estado);
           printf("Registro %s %d %.2f %s %d %s alterado\n", r[j].nome,r[j].idade,r[j].salario,r[j].ender.rua,r[j].ender.numero,r[j].ender.estado);
           ausente=0;
           }
       }
       if(ausente==1)
       {
       printf("Registro ausente para alteracao\n");
       }
    }
    }while(fgets(entrada,50,stdin) != NULL);
}
