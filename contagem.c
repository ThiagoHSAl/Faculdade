#include<stdio.h>
#include<stdlib.h>
int main ()
{
    int x=233;
    printf("%d\n",x);
    do{
        if(x<300 || x>400)
        {
        x=x+5;
        printf("%d\n", x);
        }
        else
        {
        x=x+3;
        printf("%d\n", x);
        }
    }
    while(x<457);
}