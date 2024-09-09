#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char c='b', nome[50];
    int contador=0;
    FILE *file;
    fgets(nome,sizeof(nome),stdin);
    nome[strcspn(nome, "\n")] = '\0';
    file = fopen(nome,"rb");
    while ((c=fgetc(file))  != EOF)
    {
        if (c=='a')
        contador++;
    }
    printf("%d",contador);
}
