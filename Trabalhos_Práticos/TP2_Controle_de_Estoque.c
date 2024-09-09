#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Estrutura de dados para um produto
struct produto {
    int codigo;
    char nome[50];
    int quantidade;
    float preco;
    char estado[3];
};
void ordena(int total, struct produto produtos[])
{
    for(int i=0;i<total;i++)
    {
        for (int j=i+1;j<total;j++)
        {
            if(strcmp(produtos[i].nome,produtos[j].nome)>0)
            {
                struct produto troca = produtos[i];
                produtos[i] = produtos[j];
                produtos[j] = troca;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    struct produto prod[1000];
    char linha[50];
    int quantidade_produtos, contador_linhas = 0, indice = 0, funcao;
    FILE *file;

    if (argc < 3) {
        fprintf(stderr, "Uso: %s <arquivo_entrada> <funcao> [<parametro>]\n", argv[0]);
        return 1;
    }

    // Lê o número da função a ser executada
    funcao = atoi(argv[2]);

    // Abre o arquivo de entrada
    file = fopen(argv[1], "r");
    // Lê a quantidade de produtos
    fscanf(file, "%d", &quantidade_produtos);
    fgetc(file); // Consome a nova linha após o número de produtos

    // Lê os dados dos produtos
    while (fgets(linha, sizeof(linha), file) != NULL) {
        if (contador_linhas == 5) {
            contador_linhas = 0;
            indice++;
        }
        linha[strcspn(linha, "\n")] = '\0'; // Remove nova linha
        switch (contador_linhas) {
            case 0:
                prod[indice].codigo = atoi(linha);
                break; 
            case 1:
                strcpy(prod[indice].nome, linha);
                break;
            case 2:
                prod[indice].quantidade = atoi(linha);
                break;
            case 3:
                prod[indice].preco = atof(linha);
                break;
            case 4:
                strcpy(prod[indice].estado, linha);
                break;
        }
        contador_linhas++;
    }
    fclose(file);

    // Ajusta o índice final para refletir a quantidade de produtos lidos
    if (contador_linhas > 0) {
        indice++;
    }
    // Ordena os produtos por nome
           ordena(indice,prod);

    // Executa a função solicitada
    switch (funcao) {
        case 1: 
        {
            // Abre o arquivo de saída
            file = fopen(argv[3], "w");

            // Escreve os produtos no arquivo de saída
            for (int i = 0; i < indice; i++) {
                fprintf(file, "%d\n%s\n%d\n%.2f\n%s\n", prod[i].codigo, prod[i].nome, prod[i].quantidade, prod[i].preco, prod[i].estado);
            }
            fclose(file);
            break;
        }
        case 2: {
            // Pesquisa por produto pelo código
            int codigo = atoi(argv[3]);
            for (int i = 0; i < indice; i++) {
                if (prod[i].codigo == codigo) {
                    printf("%d\n%s\n%d\n%.2f\n%s\n", prod[i].codigo, prod[i].nome, prod[i].quantidade, prod[i].preco, prod[i].estado);
                    break;
                }
            }
            break;
        }
        case 3: {
            // Lista dados do produto com menor quantidade em estoque
            int min_quantidade = prod[0].quantidade;
            int idx_min = 0;
            for (int i = 1; i < indice; i++) {
                if (prod[i].quantidade < min_quantidade) {
                    min_quantidade = prod[i].quantidade;
                    idx_min = i;
                }
            }
            printf("%d\n%s\n%d\n%.2f\n%s\n", prod[idx_min].codigo, prod[idx_min].nome, prod[idx_min].quantidade, prod[idx_min].preco, prod[idx_min].estado);
            break;
        }
        case 4: {
            // Lista produtos por estado
            char estado[3];
            strcpy(estado, argv[3]);
            struct produto produtos_estado[1000];
            int count = 0;

            for (int i = 0; i < indice; i++) {
                if (strcmp(prod[i].estado, estado) == 0) {
                    produtos_estado[count++] = prod[i];
                }
            }

            for (int i = 0; i < count; i++) {
                printf("%d\n%s\n%d\n%.2f\n%s\n", produtos_estado[i].codigo, produtos_estado[i].nome, produtos_estado[i].quantidade, produtos_estado[i].preco, produtos_estado[i].estado);
            }
            break;
        }
        case 5: {
            // Encontra produto com menor quantidade em estoque do estado
            char estado[3];
            strcpy(estado, argv[3]);
            int min_quantidade = -1;
            int idx_min = -1;

            for (int i = 0; i < indice; i++) {
                if (strcmp(prod[i].estado, estado) == 0) {
                    if (min_quantidade == -1 || prod[i].quantidade < min_quantidade) {
                        min_quantidade = prod[i].quantidade;
                        idx_min = i;
                    }
                }
            }

            if (idx_min != -1) {
                printf("%d\n%s\n%d\n%.2f\n%s\n", prod[idx_min].codigo, prod[idx_min].nome, prod[idx_min].quantidade, prod[idx_min].preco, prod[idx_min].estado);
            }
            break;
        }
        case 6: {
            // Calcula a quantidade total de itens no estoque
            int total = 0;
            for (int i = 0; i < indice; i++) {
                total += prod[i].quantidade;
            }
            printf("%d\n", total);
            break;
        }
    }

    return 0;
}