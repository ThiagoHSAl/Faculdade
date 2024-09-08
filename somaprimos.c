#include <stdio.h>
#include <stdlib.h>

int primo(long int x)
{
    long int i;
    if(x<2)
      return -1;
    for(i=2;i<x;i++)
        if(x%i==0)
        return 0;
    return 1;
}
long int soma_primos(int x)
{
    long int y=0;
    int i=0,j=2;
    while(i<x)
    {
        if(primo(j)==1)
        {
           y+=j;
           i++;
        }
       j++;
    }
    return y;
}
int main()
{
    long int x;
    int y;
    while(scanf("%d",&y)!=EOF)
    {
         x=soma_primos(y);
         printf("%ld\n",x); 
    }
  
}