#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char str1[100],str2[100];
    int tamanho, i,j=0;
    printf("digite a palavra:\n");
    fgets(str1,100,stdin);
    tamanho=strlen(str1);
    tamanho--;
      for (i=tamanho;i>=0;i--)
    {
        str2[j]=str1[i];
        j++;
    }
    
    printf("%s",str2);
}