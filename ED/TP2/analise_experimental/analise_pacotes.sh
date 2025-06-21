#!/bin/bash

# Este script automatiza a análise variando o NÚMERO de pacotes.

echo "Analisando o impacto do Número de Pacotes..."
# Configura um número fixo de armazéns para este teste
NODES_FIXO=50
sed -i "s/int nodes = [0-9]\+;/int nodes = $NODES_FIXO;/" genwkl.c

# Cria um arquivo CSV para os resultados
echo "Pacotes,TempoUser" > resultados_pacotes.csv

# Define os pontos de dados para o número de pacotes
for P in 100 200 300 400 500 600 700 800 900 1000 1100 1200 1300 1400 1500 1600 1700 1800 1900 2000 2100 2200 2300 2400 2500 2600 2700 2800 2900 3000 3100 3200 3300 3400 3500 3600 3700 3800 3900 4000 4100 4200 4300 4400 4500 4600 4700 4800 4900 5000
do
  echo "--> Testando com $P pacotes..."

  # Usa 'sed' para substituir o valor de numpackets no código fonte
  sed -i "s/int numpackets = [0-9]\+;/int numpackets = $P;/" genwkl.c

  # Recompila o gerador com os novos parâmetros
  gcc -o genwkl genwkl.c -lm
  
  # Gera o novo arquivo de entrada
  ./genwkl > input.txt
  
  # Executa o simulador e extrai o tempo 'user'
  { time ./tp2.out input.txt > /dev/null; } 2> temp_time.txt
  USER_TIME=$(grep user temp_time.txt | awk '{print $2}')
  echo "$P,${USER_TIME}" >> resultados_pacotes.csv
done

rm temp_time.txt
echo "Análise concluída! Verifique o arquivo resultados_pacotes.csv"

# Restaura o genwkl.c para um estado padrão
sed -i "s/int numpackets = [0-9]\+;/int numpackets = 100;/" genwkl.c