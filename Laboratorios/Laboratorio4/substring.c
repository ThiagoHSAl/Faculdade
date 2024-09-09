#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char str1[100],str2[100];
    int i,j,k,tamanho1,tamanho2,igual=0;
    printf("digite a primeira string:\n");
    fgets(str1,100,stdin);
    setbuf(stdin, NULL);
    printf("digite a segunda string:\n");
    fgets(str2,100,stdin);
    tamanho1=strlen(str1);
    tamanho2=strlen(str2);
    tamanho2--;
    for(i=0;i<tamanho1;i++)
    {
        if(str2[0]==str1[i])
        {
        k=0;
        j=i;
        for(k;k<tamanho2;k++)
        {
        if(str1[j]==str2[k])
        igual=1;
        else if(str1[j]!=str2[k])
        {
          igual=0;
        }
         j++;
        }
        if(igual==1)
        {
            printf("É substring\n");
            break;
        }
        }
    }
    if(igual==0)
    printf("Não é substring");
}
