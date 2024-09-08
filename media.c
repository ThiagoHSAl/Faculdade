#include <stdio.h>
#include <stdlib.h>

void media(double vet[],int n, int *i)
{
    double media,x;
    int j;
    *i=0;
    for (j=0;j<n;j++)
        media+=vet[j];
    media/=n;
    x=vet[0];
    for(j=1;j<n;j++)
        if(abs(media-vet[j])<abs(media-x))
        {
          x=vet[j];
          *i=j;
        }
}

int main()
{
   double vet[100];
   int n,i,j;

   scanf("%d",&n);
   for(j=0;j<n;j++)
    scanf("%lf",&vet[j]);
   media(vet,n,&i);
   printf("%d",i);
}
