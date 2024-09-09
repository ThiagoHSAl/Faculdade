#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum 
{
    Janeiro = 1,
    Fevereiro,
    Marco,
    Abril,
    Maio,
    Junho,
    Julho,
    Agosto,
    Setembro,
    Outubro,
    Novembro,
    Dezembro
} Mes;

struct data
{
    int dia, ano;
    Mes mes;
};

struct evento
{
    char nome[100], local[100];
    struct data Data; 
};

void cadastrar_eventos(struct evento Evento[], int n)
{
   int i,mes;
   for(i=0;i<n;i++)
   {
       scanf("%s %s %d %d %d", Evento[i].nome, Evento[i].local, &Evento[i].Data.dia, &mes, &Evento[i].Data.ano); 
       Evento[i].Data.mes=(Mes)mes;
   }
}
void imprimir_eventos(struct evento Evento[],struct data Data, int n)
{
    int verifica=0,i;
    
   for(i=0;i<n;i++)
   if(Evento[i].Data.dia==Data.dia && Evento[i].Data.mes==Data.mes && Evento[i].Data.ano==Data.ano)
   {
       verifica++;
       printf("%s %s\n",Evento[i].nome,Evento[i].local);
   }
   if (verifica==0)
   printf("Nenhum evento encontrado!");
}

int main()
{
    struct evento Evento[100];
    struct data Data;
    int n,mes;
    
    scanf("%d",&n);
    cadastrar_eventos(Evento,n);
    scanf("%d %d %d",&Data.dia,&mes,&Data.ano);
    Data.mes=(Mes)mes;
    imprimir_eventos(Evento,Data,n);
}