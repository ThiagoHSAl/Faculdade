#include <stdio.h>
#include <stdlib.h>
int main(){
	float c;
	printf ("digite a temperatura em celsius\n");
	scanf("%f", &c);
	c=c*1.8+32;
	printf("a temperatura em farenheit e %0.f", c);
	return 0;

}

