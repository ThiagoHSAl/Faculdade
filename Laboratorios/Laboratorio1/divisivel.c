#include <stdio.h>
#include <stdlib.h>
int main(){
	int x,y,z;
	printf("digite tres valores inteiros:\n");
	scanf("%d",&x);
	scanf("%d",&y);
	scanf("%d",&z);
	if (x%y==0 && x%z==0)
	printf("O número é divisível");
	else
	printf("O número não é divisível");
	return 0;
}
