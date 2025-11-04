#!/bin/bash

# --- SCRIPT DE TESTE COM COMPARAÇÃO DE SAÍDA ---
#
# Este script executa o programa com arquivos de teste que contêm
# tanto o input quanto o output esperado, separados por uma linha específica.
#
# COMO USAR:
# 1. Crie arquivos de teste (ex: test_01.txt) na pasta 'tests'.
#    Cada arquivo deve conter a entrada, seguida por uma linha com
#    '--- Expected output (text)---', e então a saída esperada.
# 2. Dê permissão de execução: chmod +x run_tests.sh
# 3. Execute o script a partir da pasta raiz do projeto: ./tests/run_tests.sh
#

# --- CONFIGURAÇÕES ---
# Cores para o output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Caminho para o executável a partir da pasta raiz
EXECUTABLE_PATH="bin/tp3.out"

# Pasta onde os testes estão localizados
TESTS_DIR="tests"

# Separador que divide o input do output esperado no arquivo de teste
SEPARATOR='--- Expected output (text)---'

# --- VERIFICAÇÕES ---
# Garante que o script está sendo executado da pasta raiz do projeto
if [ ! -d "$TESTS_DIR" ] || [ ! -f "$EXECUTABLE_PATH" ]; then
    echo -e "${RED}Erro: Este script deve ser executado da pasta raiz do projeto (TP/).${NC}"
    echo "Verifique se a pasta '$TESTS_DIR' e o executável '$EXECUTABLE_PATH' existem."
    exit 1
fi

# --- EXECUÇÃO DOS TESTES ---
# Encontra todos os arquivos de teste na pasta de testes
TEST_FILES=$(find "$TESTS_DIR" -maxdepth 1 -name "*.txt")

if [ -z "$TEST_FILES" ]; then
    echo "Nenhum arquivo de teste (.txt) encontrado na pasta '$TESTS_DIR'."
    exit 0
fi

total_tests=0
passed_tests=0

echo "Iniciando testes..."

for test_file in $TEST_FILES; do
    ((total_tests++))
    test_name=$(basename "$test_file")
    
    # 1. Extrai a parte do INPUT do arquivo de teste
    # Usa 'sed' para pegar todas as linhas até o separador
    input_data=$(sed "/$SEPARATOR/q" "$test_file")

    # 2. Extrai a parte do GABARITO (Expected Output)
    # Usa 'sed' para deletar todas as linhas desde a primeira até o separador
    expected_output=$(sed "1,/$SEPARATOR/d" "$test_file")

    # 3. Executa o programa com o input extraído
    # O C++ program espera um nome de arquivo, então criamos um temporário
    TEMP_INPUT_FILE=$(mktemp)
    echo "$input_data" > "$TEMP_INPUT_FILE"
    
    actual_output=$($EXECUTABLE_PATH "$TEMP_INPUT_FILE")
    
    rm "$TEMP_INPUT_FILE" # Limpa o arquivo temporário

    # 4. Compara a saída real com a saída esperada
    diff_result=$(diff <(echo "$actual_output") <(echo "$expected_output"))

    # 5. Reporta o resultado
    if [ -z "$diff_result" ]; then
        echo -e "[ ${GREEN}PASS${NC} ] Teste: $test_name"
        ((passed_tests++))
    else
        echo -e "[ ${RED}FAIL${NC} ] Teste: $test_name"
        echo "----------------- Diferença -----------------"
        # Fornece um diff amigável para análise do erro
        # < refere-se à saída do seu programa (actual)
        # > refere-se ao gabarito (expected)
        diff -u <(echo "$actual_output") <(echo "$expected_output")
        echo "-------------------------------------------"
    fi
done

# --- SUMÁRIO FINAL ---
echo "=========================================="
echo "Resultado Final: ${passed_tests} de ${total_tests} testes passaram."
echo "=========================================="

# Retorna um status de saída que reflete o resultado dos testes
if [ "$passed_tests" -eq "$total_tests" ]; then
    exit 0
else
    exit 1
fi