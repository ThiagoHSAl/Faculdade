#include <stdio.h>
#include <stdlib.h>

int e_primo(long int x)
{
    long int i;
    if(x<2)
      return -1;
    for(i=2;i<x;i++)
        if(x%i==0)
        return 0;
    return 1;
}
int main()
{
    long int x;
    while(scanf("%ld",&x)!=EOF)
    {
       x=e_primo(x);
       printf("%ld\n",x);
    }
}
