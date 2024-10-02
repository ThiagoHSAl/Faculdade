#include<stdio.h>
#include<stdlib.h>

int main()
{
    int fibonacci[801],i,num;
    fibonacci[0]=0;
    fibonacci[1]=1;
    for (i=2;i<=800;i++)
    {
    fibonacci[i]=fibonacci[i-1]+fibonacci[i-2];
    }
    do
    {
        printf("digite a posição desejada da sequencia\n");
        scanf("%d", &num);
        printf("%d\n",fibonacci[num]);
    }while(num>=0 && num<=800);
}