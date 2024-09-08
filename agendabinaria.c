#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct registro{
    char nome[50];
    unsigned int idade;
    char telefone[20];
};
int main()
{
    struct registro r[100];
    char entrada[50],nome[50],arquivo[50];
    int i=0,j,ausente;
    FILE *fileread;
    FILE *filewrite;
    fgets(arquivo,sizeof(arquivo),stdin);
    arquivo[strcspn(arquivo, "\n")] = '\0';
    fileread = fopen(arquivo,"rb");
    while (fread(&r[i],sizeof(struct registro),1,fileread) == 1)
    {
      i++;  
    }
    fclose(fileread);
    while(fgets(entrada,50,stdin)!=NULL)
    
    {
       entrada[strcspn(entrada,"\n")]='\0'; 
       if (strcmp("Inserir",entrada)==0)
       {
          if(i<100)
          {
           scanf("%s %d %s",r[i].nome,&r[i].idade,r[i].telefone);
           printf("Registro %s %d %s inserido\n", r[i].nome,r[i].idade,r[i].telefone);
           i++;
        }
        else
        {
           printf("Espaco insuficiente\n");
        }
    }
       else if (strcmp("Exibir",entrada)==0)
       {
         ausente=1;
         scanf("%s",nome);
          for(j=0;j<100;j++)
           {
             if(strcmp(r[j].nome,nome)==0)
             {
               printf("Registro %s %d %s exibido\n", r[j].nome,r[j].idade,r[j].telefone);
               ausente=0;
             }
           }
             if(ausente==1)
            {
             printf("Registro %s invalido\n",nome);
            }
        }
         else if (strcmp("Alterar",entrada)==0)
        {
          ausente=1;
          scanf("%s",nome);
          for(j=0;j<100;j++)
           if(strcmp(r[j].nome,nome)==0)
            {
             scanf("%s %d %s",r[i].nome,&r[i].idade,r[i].telefone);
             printf("Registro %s %d %s alterado\n", r[j].nome,r[j].idade,r[i].telefone);
             ausente=0;
            }
          if(ausente==1)
          printf("Registro %s invalido\n",nome);
        }
    else if (strcmp("Excluir",entrada)==0)
        {
            ausente=1;
            scanf("%s",nome);
            for(j=0;j<100;j++)
           {
               if(strcmp(r[j].nome,nome)==0)
               {  
                printf("Registro %s %d %s excluido\n", r[j].nome,r[j].idade,r[j].telefone);   
                strcpy(r[j].nome,r[i].nome);
                r[j].idade=r[i].idade;
                strcpy(r[j].telefone,r[i].telefone);
                strcpy(r[i].nome," ");
                r[i].idade=0;
                strcpy(r[i].telefone," ");
                i--;
                 ausente=0;
               }
           }
           if(ausente==1)
             {
               printf("Registro %s invalido\n",nome);
             }
        }
    }
    filewrite = fopen("saida.bin","wb");
    fwrite(r,sizeof(struct registro),i,filewrite);
    fclose(filewrite);
}