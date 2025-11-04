#!/bin/bash

# --- Configurações ---
# Pastas de teste
PASTA_INPUTS="inputs"
PASTA_OUTPUTS="outputs"
EXECUTAVEL="../tp1.out"

# --- Cores para o output ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # Sem Cor

# --- 2. Execução dos Testes ---
# Inicializa os contadores
total_testes=0
testes_passaram=0

# Verifica se a pasta de inputs existe
if [ ! -d "$PASTA_INPUTS" ]; then
    echo -e "${RED}Erro: Pasta de inputs '$PASTA_INPUTS' não encontrada!${NC}"
    exit 1
fi

# Loop por todos os arquivos na pasta de inputs
for arquivo_input in "$PASTA_INPUTS"/*; do
    # Incrementa o contador total de testes
    ((total_testes++))

    # Extrai o nome base do arquivo (ex: teste01)
    nome_base_input=$(basename "$arquivo_input")
    nome_base_output="${nome_base_input/in/out}"
    # Monta o caminho para o arquivo de output esperado
    arquivo_output_esperado="$PASTA_OUTPUTS/$nome_base_output"

    # Verifica se o arquivo de output esperado correspondente existe
    if [ ! -f "$arquivo_output_esperado" ]; then
        echo -e "${YELLOW}AVISO: Arquivo de output esperado '$arquivo_output_esperado' não encontrado para o input '$nome_base'. Pulando teste.${NC}"
        continue
    fi
    
    echo "Executando teste: $nome_base"

    # Executa o programa, redirecionando o input e capturando o output real
    # O comando diff compara os dois arquivos. O -w ignora diferenças de espaços em branco.
    # A saída do diff é suprimida com > /dev/null
    if diff -w <(./$EXECUTAVEL < "$arquivo_input") "$arquivo_output_esperado" > /dev/null; then
        # Se diff não encontrar diferenças, o exit code é 0 (sucesso)
        echo -e "  └─ ${GREEN}PASSOU${NC}"
        ((testes_passaram++))
    else
        # Se diff encontrar diferenças, o exit code é diferente de 0 (falha)
        echo -e "  └─ ${RED}FALHOU${NC}"
        echo "     --- Diferenças ---"
        # Mostra as diferenças para o usuário poder depurar
        diff -y -W 80 --suppress-common-lines <(./$EXECUTAVEL < "$arquivo_input") "$arquivo_output_esperado"
        echo "     ------------------"
    fi
done

# --- 3. Relatório Final ---
echo "-----------------------------------------"
echo "Relatório Final:"
if [ "$total_testes" -eq "$testes_passaram" ]; then
    echo -e "${GREEN}Todos os $total_testes testes passaram! Excelente!${NC}"
else
    echo -e "${YELLOW}$testes_passaram / $total_testes testes passaram.${NC}"
fi
echo "-----------------------------------------"
