#include <stdio.h>
#include <stdlib.h>

void primos(int m, int *p1, int *p2)
{
 int i,j,primo;
     for(i=m-1;i>=2;i--)
    {
    primo=1;
    for(j=3;j<i;j++)
      if(i%j==0)
      primo=0;
    if (primo==1)
    break;
    }
  *p1=i;

 j=m;
do
{
  j++;
  primo=1;
  for(i=2;i<j;i++)
    if(j%i==0)
    primo=0;
}while(primo!=1);
*p2=j;
}
int main()
{
   int m,p1,p2;

   scanf("%d",&m);
   primos(m,&p1,&p2);
   printf("%d\n%d",p1,p2);
}
