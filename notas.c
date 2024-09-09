#include <stdio.h>
#include <stdlib.h>
int main(){
	int n,nota100,nota50,nota20,nota10,nota5,nota2;
	printf("digite o montante em reais:\n");
	scanf("%d",&n);
	
    nota100=n/100;
    
    n=n%100;
    
    nota50=n/50;
    
    n=n%50;
    
    nota20=n/20;
    
    n=n%20;
    
    nota10=n/10;
    
    n=n%10;
    
    nota5=n/5;
    
    n=n%5;
    
    nota2=n/2; 
    
    n=n%2;
     printf("100:%d\n50:%d\n20:%d\n10:%d\n5:%d\n2:%d\n1:%d", nota100,nota50,nota20,nota10,nota5,nota2,n);
    return 0;
}
