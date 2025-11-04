#!/bin/bash

# Este script para a execução se qualquer comando falhar.
set -e

# --- SCRIPT DE ANÁLISE EXPERIMENTAL FINAL ---
#
# Versão com configurações de experimento personalizadas.
#

echo "--- INICIANDO ANÁLISE EXPERIMENTAL COM NOVAS CONFIGURAÇÕES ---"
echo "Diretório de execução: $(pwd)"


# --- CONFIGURAÇÕES ---
EXECUTAVEL_TP3="../bin/tp3.out"
EXECUTAVEL_SCHED="./sched"
ARQUIVO_C_GERADOR="genwkl3.c"
ARQUIVO_C_BACKUP="genwkl3.c.master_bak" 
RELATORIOS_DIR="relatorios"
REPETICOES=5

# --- VERIFICAÇÕES INICIAIS E BACKUP ---
if [ ! -f "$EXECUTAVEL_TP3" ]; then
    echo "ERRO: Executável principal '$EXECUTAVEL_TP3' não encontrado."
    exit 1
fi
if [ ! -f "$EXECUTAVEL_SCHED" ]; then
    echo "ERRO: Executável '$EXECUTAVEL_SCHED' não encontrado."
    exit 1
fi
if [ ! -f "$ARQUIVO_C_GERADOR" ]; then
    echo "ERRO: Arquivo gerador '$ARQUIVO_C_GERADOR' não encontrado."
    exit 1
fi

mkdir -p "$RELATORIOS_DIR"
# CRIA UM BACKUP MESTRE DO ARQUIVO ORIGINAL ANTES DE QUALQUER MUDANÇA
cp "$ARQUIVO_C_GERADOR" "$ARQUIVO_C_BACKUP"


# --- FUNÇÃO PRINCIPAL DO EXPERIMENTO ---
# A função agora confia que os parâmetros fixos já foram definidos.
run_experiment() {
    local ATRIBUTO="$1"
    local VALORES="$2"
    local RELATORIO_FILE="$RELATORIOS_DIR/relatorio_$ATRIBUTO.txt"
    local ARQUIVO_C_TEMP_BAK="genwkl3.c.temp_bak"

    echo ""
    echo "=========================================================="
    echo "===> TESTANDO ATRIBUTO: $ATRIBUTO"
    echo "=========================================================="

    echo "# Relatório de Desempenho para o atributo: $ATRIBUTO" > "$RELATORIO_FILE"
    echo "# Valor | Tempo_Medio_ms" >> "$RELATORIO_FILE"
    
    # Cria um backup do estado pré-configurado para este experimento específico
    cp "$ARQUIVO_C_GERADOR" "$ARQUIVO_C_TEMP_BAK"

    for VALOR in $VALORES; do
        echo ""
        echo "--> Preparando teste para $ATRIBUTO = $VALOR..."
        # Restaura o estado pré-configurado e aplica a mudança do valor atual
        cp "$ARQUIVO_C_TEMP_BAK" "$ARQUIVO_C_GERADOR"
        sed -i "s/int $ATRIBUTO = [0-9]\+;/int $ATRIBUTO = $VALOR;/" "$ARQUIVO_C_GERADOR"
        echo "    Arquivo $ARQUIVO_C_GERADOR modificado."

        local total_time=0.0

        for i in $(seq 1 $REPETICOES); do
            echo "    Executando repetição $i de $REPETICOES..."
            # --- Pipeline ---
            gcc -o genwkl3 "$ARQUIVO_C_GERADOR" -lm
            ./genwkl3
            ./"$EXECUTAVEL_SCHED" < tp2.wkl > sched.log 2> sched.err
            sed -f tp2tp3.sed sched.log | awk -f intp3.awk > tmptp3.out
            cat tp3.wkl tmptp3.out | sort > tp3.in
            rm tmptp3.out
            # --- Medição ---
            sleep 0.1
            local exec_time
            exec_time=$(/usr/bin/time -p "$EXECUTAVEL_TP3" "tp3.in" 2>&1 >/dev/null | grep real | awk '{print $2}')
            total_time=$(echo "$total_time + $exec_time" | bc)
        done

        local avg_time_ms
        avg_time_ms=$(echo "scale=4; ($total_time / $REPETICOES) * 1000" | bc)
        echo "    --> RESULTADO: Valor: $VALOR, Tempo Médio: ${avg_time_ms} ms"
        echo "$VALOR $avg_time_ms" >> "$RELATORIO_FILE"
    done
    
    # Limpa o backup temporário deste experimento
    rm "$ARQUIVO_C_TEMP_BAK"
}

# --- DEFINIÇÃO DOS EXPERIMENTOS COM CONFIGURAÇÕES PERSONALIZADAS ---

# Teste 1: Variando 'nodes'
echo -e "\nConfigurando para o Experimento 1: nodes..."
cp "$ARQUIVO_C_BACKUP" "$ARQUIVO_C_GERADOR" # Restaura para o original
sed -i "s/int numpackets = [0-9]\+;/int numpackets = 400;/" "$ARQUIVO_C_GERADOR"
sed -i "s/int numclients = [0-9]\+;/int numclients = 100;/" "$ARQUIVO_C_GERADOR"
run_experiment "nodes" "5 7 8 9 10"

# Teste 2: Variando 'numpackets'
echo -e "\nConfigurando para o Experimento 2: numpackets..."
cp "$ARQUIVO_C_BACKUP" "$ARQUIVO_C_GERADOR" # Restaura para o original
sed -i "s/int nodes = [0-9]\+;/int nodes = 10;/" "$ARQUIVO_C_GERADOR"
sed -i "s/int numclients = [0-9]\+;/int numclients = 100;/" "$ARQUIVO_C_GERADOR"
run_experiment "numpackets" "$(seq 10 20 900)"

# Teste 3: Variando 'numclients'
echo -e "\nConfigurando para o Experimento 3: numclients..."
cp "$ARQUIVO_C_BACKUP" "$ARQUIVO_C_GERADOR" # Restaura para o original
sed -i "s/int nodes = [0-9]\+;/int nodes = 10;/" "$ARQUIVO_C_GERADOR"
sed -i "s/int numpackets = [0-9]\+;/int numpackets = 400;/" "$ARQUIVO_C_GERADOR"
run_experiment "numclients" "$(seq 2 1 25)"


# --- LIMPEZA FINAL ---
# Remove o backup mestre e restaura o arquivo original para o estado inicial
rm "$ARQUIVO_C_GERADOR"
mv "$ARQUIVO_C_BACKUP" "$ARQUIVO_C_GERADOR"
echo ""
echo "--- ANÁLISE EXPERIMENTAL CONCLUÍDA ---"
echo "Relatórios foram salvos no diretório: $RELATORIOS_DIR"