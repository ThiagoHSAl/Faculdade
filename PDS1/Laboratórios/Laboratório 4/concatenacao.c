#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main()
{
    char str1[100], str2[100];
    printf("digite a primeira palavra:\n");
    scanf("%s",str1);
    printf("digite a segunda palavra:\n");
    setbuf(stdin, NULL);
    scanf("%s", str2);
    strcat(str1,str2);
    printf("%s",str1);
}