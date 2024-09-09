#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    char c='b';
    int contador=0;
    FILE *file;
    
    file = fopen(argv[1],"r");
    while ((c=fgetc(file))  != EOF)
    {
        if (c=='a')
        contador++;
    }
    printf("%d",contador);
}