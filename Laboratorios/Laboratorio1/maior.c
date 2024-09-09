#include <stdio.h>
#include <stdlib.h>
int main(){
	int x,y,z;
	printf("digite tres valores inteiros:\n");
	scanf("%d",&x);
	scanf("%d",&y);
	scanf("%d",&z);
	if (x>y && x>z)
	printf("o maior valor e %d", x);
	else if (y>z)
	printf("o maior valor e %d", y);
	else
	printf("o maior valor e %d", z);
	return 0;
}
