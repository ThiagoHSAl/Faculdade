#include <stdio.h>
#include <stdlib.h>
int main(){
    int x0, x1, i, termos, xn;
    printf("digite quantos termos tera sua sequencia\n");
    scanf("%d", &termos);
    printf("digite x0 e x1\n");
    scanf("%d", &x0);
    scanf("%d", &x1);
    printf("x0:%d\nx1:%d\n",x0,x1);
    for(i=2; i<=termos; i++)
    {
       xn=4*x1-2*x0; 
       printf("x%d:%d\n",i, xn);
       x0=x1;
       x1=xn;
    }
}
  