#include<stdio.h>
#include<stdlib.h>
#include<math.h>
int main()
{
    double x=M_PI, precisao, p=4, y=3;
    int i, z=0, fator=1;
    printf("digite sua precisão\n");
    scanf("%lf", &precisao);
    for(i=1; z==0; i++)
    {
        p=p-fator*(4/y);
        fator=-1*fator;
        y=y+2;
        if(p<=x+precisao && p>=x-precisao)
        z=1;
    }
    printf("%d\n", i);
}
