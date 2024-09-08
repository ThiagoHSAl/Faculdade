#include<stdio.h>
#include<stdlib.h>
int main ()
{
    int multiplos2=0, multiplos3=0, multiplos5=0, multiplos=0, x, i=1;
    printf("digite x\n");
    scanf("%d", &x);
    do{
        if(i%2==0)
        multiplos2++;
        if(i%3==0)
        multiplos3++;
        if(i%5==0)
        multiplos5++;
        if(i%2==0 && i%3==0 && i%5==0)
        multiplos++;
        
        i++;
    }
    while(i<=x);
    printf("\nMúltiplos de 2:%d\nMúltiplos de 3:%d\nMúltiplos de 5:%d\nMúltiplos de todos:%d", multiplos2, multiplos3, multiplos5, multiplos);
}