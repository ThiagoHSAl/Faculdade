#include <stdio.h>
#include <math.h>

struct Iris
{
    float cs,ls,cp,lp;
    char tipo[50];
};

struct Iris_nao_identificada
{
    float cs,ls,cp,lp;
};

void classificar(struct Iris_nao_identificada ini, struct Iris iris[], int n)
{
    int indexador=0;
    float identificador,comparador;
    
    identificador=sqrt(pow((ini.cs-iris[0].cs),2)+pow((ini.ls-iris[0].ls),2)+pow((ini.cp-iris[0].cp),2)+pow((ini.lp-iris[0].lp),2));
    for(int i=1;i<n;i++)
    {
        comparador=sqrt(pow((ini.cs-iris[i].cs),2)+pow((ini.ls-iris[i].ls),2)+pow((ini.cp-iris[i].cp),2)+pow((ini.lp-iris[i].lp),2));
        if(comparador<identificador)
        {
            identificador=comparador;
            indexador=i;
        }
    }
    printf("%s",iris[indexador].tipo);
}

int main()
{
    struct Iris iris[500];
    struct Iris_nao_identificada ini;
    int n;
    
    scanf("%d",&n);
    for (int i=0;i<n;i++)
    scanf("%f %f %f %f %s",&iris[i].cs,&iris[i].ls,&iris[i].cp,&iris[i].lp,iris[i].tipo);
    scanf("%f %f %f %f",&ini.cs,&ini.ls,&ini.cp,&ini.lp);
    classificar(ini,iris,n);
}
