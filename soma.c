#include <stdio.h>
#include <stdlib.h>
int main ()
{
    int x, i, num=0;
    printf("digite x\n");
    scanf("%d", &x);
    for (i=1;i<=x;i++)
    {
        num=num+i;
    }
    printf("%d",num);
}