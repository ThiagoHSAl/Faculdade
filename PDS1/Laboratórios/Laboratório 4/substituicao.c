#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char str1[100],c1,c2;
    int i,tamanho;
    printf("digite a palavra:\n");
    fgets(str1,100,stdin);
    printf("digite os caracteres 1 e 2:\n");
    scanf("%c %c",&c1,&c2);
    tamanho=strlen(str1);
    for(i=0;i<tamanho;i++)
    {
        if(str1[i]==c1)
        {
            str1[i]=c2;
            break;
        }
    }
    printf("%s",str1);
}