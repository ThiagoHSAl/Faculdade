# compila genwkl3
gcc -o genwkl3 genwkl3.c -lm
# genwkl gera 2 arquivos: tp2.wkl (entrada para tp2) e tp3.wkl
./genwkl3
# execute o tp2 (nomeado sched) que le stdin e gera saida em sched.log
./sched < tp2.wkl
# reformata a saida do tp2 para entrada do tp3
sed -f tp2tp3.sed sched.log | awk -f intp3.awk > tmptp3.out
#concatena os eventos do tp3 com a saida reformatada do tp2 e ordena
cat tp3.wkl tmptp3.out | sort > tp3.in
#remove o arquivo temporario
rm tmptp3.out
