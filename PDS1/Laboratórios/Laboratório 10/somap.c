#include <stdio.h>
#include <stdlib.h>

void somavetor(int *v1, int *v2, int *v3, int n)
{
    for(int i=0;i<n;i++)
        v3[i]=v1[i]+v2[i];
}
int main()
{
    int *v1,*v2,*v3,i,n;

    scanf("%d",&n);
    v1=(int *)malloc(n*sizeof(int));
    v2=(int *)malloc(n*sizeof(int));
    v3=(int *)malloc(n*sizeof(int));
    for(i=0;i<n;i++)
    scanf("%d",&v1[i]);
    for(i=0;i<n;i++)
    scanf("%d",&v2[i]);
    somavetor(v1,v2,v3,n);
    for(i=0;i<n;i++)
        printf("%d\n",v3[i]);
    free(v1);
    free(v2);
    free(v3);
}
