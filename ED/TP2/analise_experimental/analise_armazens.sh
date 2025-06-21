#!/bin/bash

# Este script automatiza a análise variando o número de armazéns.
# Certifique-se de que genwkl.c, tp2.out e este script estejam no mesmo diretório.

echo "Analisando o impacto do Número de Armazéns..."
# Cria um arquivo CSV para os resultados
echo "Armazens,TempoUser" > resultados_armazens.csv

# Define os pontos de dados para o número de armazéns
for N in 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190 200 210 220 230 240 250 260 270 280 290 300 310 320 330 340 350 360 370 380 390 400 410 420 430 440 450 460 470 480 490 500

do
  echo "--> Testando com $N armazens..."
  
  # Calcula um número proporcional de pacotes
  NUM_PACOTES=$((N * 10))

  # Usa 'sed' para substituir os valores no código fonte do gerador
  sed -i "s/int nodes = [0-9]\+;/int nodes = $N;/" genwkl.c
  sed -i "s/int numpackets = [0-9]\+;/int numpackets = $NUM_PACOTES;/" genwkl.c

  # Recompila o gerador com os novos parâmetros
  gcc -o genwkl genwkl.c -lm
  
  # Gera o novo arquivo de entrada
  ./genwkl > input.txt
  
  # Executa o simulador com 'time' e redireciona a saída para extrair o tempo 'user'
  # A saída padrão do simulador é descartada com '> /dev/null'
  { time ./tp2.out input.txt > /dev/null; } 2> temp_time.txt
  
  # Extrai o tempo 'user' e anexa ao arquivo CSV
  USER_TIME=$(grep user temp_time.txt | awk '{print $2}')
  echo "$N,${USER_TIME}" >> resultados_armazens.csv
done

# Limpa o arquivo temporário
rm temp_time.txt
echo "Análise concluída! Verifique o arquivo resultados_armazens.csv"

# Restaura o genwkl.c para um estado padrão (opcional)
sed -i "s/int nodes = [0-9]\+;/int nodes = 10;/" genwkl.c
sed -i "s/int numpackets = [0-9]\+;/int numpackets = 100;/" genwkl.c