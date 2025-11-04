#!/bin/bash

# Script para compilar e simular o módulo 'cipher_bonus' com diferentes
# larguras para o PLAINTEXT_WIDTH, passadas via linha de comando.

echo "Iniciando bateria de testes automatizados..."

# Defina aqui todos os tamanhos de plaintext que você quer testar
widths_to_test=(13 24 32 40 64)

# Itera sobre cada largura definida no array acima
for width in "${widths_to_test[@]}"
do
  echo ""
  echo "====================================================="
  echo "    Testando com PLAINTEXT_WIDTH = $width"
  echo "====================================================="
  
  # Compila o código, passando o parâmetro de largura via linha de comando
  # A flag -P faz a "mágica" de sobrescrever o parâmetro do testbench
  iverilog -g2012 \
           -o simulation_output \
           -P cipher_bonus_tb.PLAINTEXT_WIDTH=$width \
           cipher_bonus.v cipher_bonus_tb.v
           
  # Se a compilação foi bem-sucedida, executa a simulação
  if [ $? -eq 0 ]; then
    vvp simulation_output
  else
    echo ">>>> ERRO DE COMPILAÇÃO para a largura $width. Abortando teste."
    exit 1
  fi
  
done

echo ""
echo "====================================================="
echo "Bateria de testes concluída."
echo "====================================================="