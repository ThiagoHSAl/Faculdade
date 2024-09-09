#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct produto{
    char nome[50],marca[50];
    double preco;
};
struct print{
    char marca[50];
    double media;
    int contador;
};
int main(){
    struct produto prod[8];
    struct print p[8];
    int i,j,posicao=0;
    double media_total=0,contador;
    
    for(i=0;i<8;i++)
    {
        scanf("%s %s %lf",prod[i].nome,prod[i].marca,&prod[i].preco);
        media_total+=prod[i].preco;
    }
    media_total/=8;
    for(i=0;i<8;i++)
    {
    if(strcmp(prod[i].marca,"x")!=0)
    {
    strcpy(p[posicao].marca,prod[i].marca);
    p[posicao].media=prod[i].preco;
    contador=1;
       for(j=i+1;j<8;j++)
       {
        if(strcmp(prod[i].marca,prod[j].marca)==0)
        {
        contador++;
        strcpy(prod[j].marca,"x");
        p[posicao].media+=prod[j].preco;
        }
       }
       p[posicao].media=p[posicao].media/contador;
       p[posicao].contador=contador;
       posicao++;
    }
    }
    for(i=0;i<posicao;i++)
    printf("%s %d\n",p[i].marca,p[i].contador);
    printf("media total %.2f\n",media_total);
    for(i=0;i<posicao;i++)
    printf("media %s %.2f\n",p[i].marca,p[i].media);
}
