#include<stdio.h>
#include<stdlib.h>
int main ()
{
  int intervalo1, intervalo2, n,i,j,troca;
  printf("digite seu intervalo\n");
do
  {
    scanf("%d",&intervalo1);
    if(intervalo1<0 || intervalo1>=10000)
    printf("os números tem que ser inteiros, positivos e menores que 10000\n");
  }
  while(intervalo1<0 || intervalo1 >=10000);
do
  {
    scanf("%d",&intervalo2);
    if(intervalo2<0 || intervalo2>=10000)
      printf("os números tem que ser inteiros, positivos e menores que 10000\n");
  }
  while(intervalo2<0 || intervalo2>=10000);
if(intervalo2 <intervalo1 )
  {
    troca=intervalo1;
    intervalo1=intervalo2;
    intervalo2=troca;
  }
for(j=intervalo1;j<=intervalo2;j++)
  {
    n=j;
    for(i=2;i<j;i++)
      {
        if(n%i==0)
        n=0;
      }
    if(n!=0 && n!=1)
      printf("%d\n",n);
  }
}
