#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char nome[50];
    long int matriz1[5][5], matriz2[5][5];
    int i, j;
    FILE *file;
    

    fgets(nome, sizeof(nome), stdin);
    nome[strcspn(nome, "\n")] = '\0'; 
    file = fopen(nome, "rb");
   
   for (i = 0; i < 5; i++) {
        for (j = 0; j < 5; j++) {
             fscanf(file,"%ld",&matriz1[i][j]);
        }
    }
   
    for (i = 0; i < 5; i++) {
        for (j = 0; j < 5; j++) {
             fscanf(file,"%ld",&matriz2[i][j]);
        }
    }
    fclose(file);
    for (i = 0; i < 5; i++) {
        for (j = 0; j < 5; j++) {
            matriz1[i][j] += matriz2[i][j];
            printf("%ld ", matriz1[i][j]);
        }
        printf("\n");
    }
    
}