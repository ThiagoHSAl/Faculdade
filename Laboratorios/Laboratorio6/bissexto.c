#include <stdio.h>
#include <stdlib.h>

int bissexto(int x)
{
      if((x%4==0 && x%100!=0) || (x%400==0))
        return 1;
      else
        return 0;
}
int main()
{
    int x;
    while(scanf("%d",&x)!=EOF)
    {
        x=bissexto(x);
        printf("%d\n",x);
    }
}
