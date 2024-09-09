#include <stdio.h>
#include <stdlib.h>

int bissexto(int x)
{
      if((x%4==0 && x%100!= 0) || (x%400== 0))
        return 1;
      else
        return 0;
}

int quantos_dias(int dia, int mes, int ano)
{
int dias=0;
while(ano<=2020)
{
if(mes==1 || mes==3 || mes==5 || mes==7 ||  mes==8 || mes==10 || mes==12)
{
  dias+=31;
  if(mes==12)
  {
      ano++;
      mes=1;
  }
  else mes++;
}
if(mes==2)
{
 dias+=28;
  if(bissexto(ano)==1)
    dias++;
  mes++;
}
if(mes==4 || mes==6 || mes==9 || mes==11)
{
      if(mes==9 && ano==2020)
      {
        dias+=18;
        return dias;
      }
    dias+=30;
  mes++;
}
}
}
int main()
{
     int dia,mes,ano,dias;
     while (scanf("%d %d %d",&dia,&mes,&ano) != EOF)
     {
          dias=quantos_dias(dia,mes,ano);
          dias-=dia;
          printf("%d\n",dias);
          dias=0;
       }

}
