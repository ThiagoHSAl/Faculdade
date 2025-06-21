#!/bin/bash

# Este script automatiza a análise variando a CAPACIDADE de transporte.

echo "Analisando o impacto da Capacidade de Transporte..."
# Configura valores fixos
NODES_FIXO=500
PACOTES_FIXO=5000
sed -i "s/int nodes = [0-9]\+;/int nodes = $NODES_FIXO;/" genwkl.c
sed -i "s/int numpackets = [0-9]\+;/int numpackets = $PACOTES_FIXO;/" genwkl.c

# Cria arquivo de resultados
echo "Capacidade,TempoUser" > resultados_capacidade.csv

# Aumentar a capacidade deve diminuir a contenção
for C in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
do
  echo "--> Testando com capacidade = $C..."

  # Altera a variável transportcapacity no gerador
  sed -i "s/int transportcapacity = [0-9]\+;/int transportcapacity = $C;/" genwkl.c

  # Recompila e gera
  gcc -o genwkl genwkl.c -lm
  ./genwkl > input.txt
  
  # Executa e mede
  { time ./tp2.out input.txt > /dev/null; } 2> temp_time.txt
  USER_TIME=$(grep user temp_time.txt | awk '{print $2}')
  echo "$C,${USER_TIME}" >> resultados_capacidade.csv
done

rm temp_time.txt
echo "Análise concluída! Verifique o arquivo resultados_capacidade.csv"

# Restaura o padrão
sed -i "s/int transportcapacity = [0-9]\+;/int transportcapacity = 2;/" genwkl.c