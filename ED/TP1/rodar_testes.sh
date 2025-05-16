#!/bin/bash

EXEC="./bin/tp1.out"
DIRETORIO_TESTES="./tests"
ARQUIVOS=$(ls "$DIRETORIO_TESTES"/*.txt)

echo "🔎 Rodando testes..."

for arquivo in $ARQUIVOS; do
    echo "----------------------------------------"
    echo "🧪 Testando: $arquivo"

    input_temp="input_temp.txt"
    output_temp="saida_temp.txt"
    esperado_temp="esperado_temp.txt"

    # Extrai o input
    sed -n '/###### start input file ######/,/###### end input file ######/p' "$arquivo" | sed '1d;$d' > "$input_temp"

    # Extrai o output esperado
    awk '/###### end input file ######/ {flag=1; next} flag' "$arquivo" > "$esperado_temp"

    # Executa o programa
    $EXEC "$input_temp" > "$output_temp"

    # Compara diretamente as saídas
    if diff -q "$output_temp" "$esperado_temp" > /dev/null; then
        echo "✅ Teste passou"
    else
        echo "❌ Teste falhou"
        echo "🔍 Diferenças:"
        diff -y --suppress-common-lines "$output_temp" "$esperado_temp"
    fi

    # Remove arquivos temporários
    rm -f "$input_temp" "$output_temp" "$esperado_temp"
done

echo "✅ Fim dos testes."
