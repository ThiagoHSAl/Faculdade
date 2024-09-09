#include <stdio.h>
#include <stdlib.h>

void preenche(int v[],int n)
{
    for(int i=0;i<n;i++)
        scanf("%d",&v[i]);
}
int main()
{
    int n,*v,i;
    scanf("%d",&n);
    v=(int *)malloc(n*sizeof(int));
    preenche(v,n);
    for(i=0;i<n;i++)
        printf("%d\n",v[i]);
    free(v);
}
