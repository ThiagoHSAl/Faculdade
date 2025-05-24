Respostas da Lista de Exercícios - Introdução a Sistemas Lógicos

1.  **Diferença entre Circuitos Combinacionais e Sequenciais:**
    * **Circuitos Combinacionais:** A saída depende exclusivamente das combinações das entradas atuais. Eles não possuem memória.
        * Exemplos: Somadores, subtratores, multiplexadores (MUX), demultiplexadores (DEMUX), codificadores, decodificadores, comparadores.
    * **Circuitos Sequenciais:** A saída depende das entradas atuais e do estado anterior do circuito (ou seja, das saídas anteriores). Eles possuem elementos de memória.
        * Exemplos: Flip-flops (como D, JK, T, SR), registradores, contadores, memórias RAM/ROM.

2.  **Flip-Flop Tipo D:**
    * **Diagrama de Blocos (Esquemático):**
        Um flip-flop tipo D possui tipicamente as seguintes entradas e saídas:
        * Entrada D (Dados)
        * Entrada CLK (Clock)
        * Saída Q
        * Saída Q' (Q barrado - o complemento de Q)
        (Um diagrama mostraria um bloco retangular com D e CLK como entradas e Q e Q' como saídas.)
    * **Funcionamento Básico:** O flip-flop tipo D é um dispositivo de memória básico que armazena o valor presente na entrada D quando ocorre uma transição ativa do sinal de clock (geralmente borda de subida ou descida). Se a entrada D for '1' na borda ativa do clock, a saída Q se torna '1'. Se D for '0', Q se torna '0'. A saída Q mantém esse valor até a próxima borda ativa do clock.
    * **Onde é Comumente Utilizado:** É fundamental em registradores de dados (para armazenar palavras binárias), memórias, contadores síncronos, e para sincronização de sinais em sistemas digitais.

3.  **Registrador de 4 bits após Rotações à Esquerda:**
    * Palavra binária inicial: 1101
    * **Após a primeira rotação à esquerda com entrada de 1 bit (assumindo que o bit de entrada é '1' e entra pela direita):**
        O bit mais à esquerda (MSB) é perdido (ou pode ser capturado por outro circuito), os bits restantes se movem uma posição para a esquerda, e o novo bit de entrada ('1') entra na posição mais à direita (LSB).
        Conteúdo inicial:  1  1  0  1
        Após rotação 1: (1) 1  0  1  <- 1  (O '1' mais à esquerda é perdido, '1' entra pela direita)
        Conteúdo: 1011
    * **Após a segunda rotação à esquerda com entrada de 1 bit ('1'):**
        Conteúdo antes da rotação 2: 1011
        Após rotação 2: (1) 0  1  1  <- 1
        Conteúdo: 0111
    * Conteúdo final do registrador após duas rotações à esquerda com entrada de '1': 0111.

4.  **Projeto de Circuito Sequencial com Flip-Flops JK:**
    Sequência desejada: $00 \rightarrow 01 \rightarrow 11 \rightarrow 10 \rightarrow 00...$
    Utilizaremos dois flip-flops JK, $Q_1$ (MSB) e $Q_0$ (LSB).

    1.  **Tabela de Transição de Estados:**
        | Estado Atual ($Q_1Q_0$) | Próximo Estado ($Q_1^+Q_0^+$) |
        |------------------------|-----------------------------|
        | 00                     | 01                          |
        | 01                     | 11                          |
        | 11                     | 10                          |
        | 10                     | 00                          |

    2.  **Tabela de Excitação para Flip-Flops JK (Q -> Q$^+$ | J K):**
        | Q  | Q$^+$ | J  | K  |
        |----|-------|----|----|
        | 0  | 0     | 0  | X  | (X = Não importa)
        | 0  | 1     | 1  | X  |
        | 1  | 0     | X  | 1  |
        | 1  | 1     | X  | 0  |

    3.  **Derivação das Entradas J e K para cada Flip-Flop:**
        * Para $FF_1$ (saída $Q_1$):
            | $Q_1$ | $Q_0$ | $Q_1^+$ | $J_1$ | $K_1$ |
            |-------|-------|---------|-------|-------|
            | 0     | 0     | 0       | 0     | X     |
            | 0     | 1     | 1       | 1     | X     |
            | 1     | 1     | 1       | X     | 0     |
            | 1     | 0     | 0       | X     | 1     |
            Das tabelas K (ou por inspeção): $J_1 = Q_0$; $K_1 = \overline{Q_0}$ (ou $Q_0$ invertido)

        * Para $FF_0$ (saída $Q_0$):
            | $Q_1$ | $Q_0$ | $Q_0^+$ | $J_0$ | $K_0$ |
            |-------|-------|---------|-------|-------|
            | 0     | 0     | 1       | 1     | X     |
            | 0     | 1     | 1       | X     | 0     |
            | 1     | 1     | 0       | X     | 1     |
            | 1     | 0     | 0       | 0     | X     |
            Das tabelas K (ou por inspeção): $J_0 = \overline{Q_1}$; $K_0 = Q_1$

    4.  **Diagrama do Circuito:**
        (O diagrama consistiria em dois flip-flops JK. O clock seria comum a ambos. As conexões seriam:
        Para $FF_1$: $J_1$ conectado a $Q_0$; $K_1$ conectado a $\overline{Q_0}$ (saída $Q_0$ passando por uma porta NOT).
        Para $FF_0$: $J_0$ conectado a $\overline{Q_1}$; $K_0$ conectado a $Q_1$.
        As saídas do circuito são $Q_1$ e $Q_0$.)

5.  **Tabela de Transição de Estados para um Flip-Flop T:** [cite: 9]
    Um flip-flop T (Toggle) muda seu estado de saída (toggle) se a entrada T for '1' na borda ativa do clock. Se T for '0', a saída mantém seu estado atual.

    | Estado Atual (Q) | Entrada T | Próximo Estado (Q$^+$) |
    |------------------|-----------|-----------------------|
    | 0                | 0         | 0                     |
    | 0                | 1         | 1                     |
    | 1                | 0         | 1                     |
    | 1                | 1         | 0                     |

6.  **Conceito de Máquina de Estados Finitos (FSM):** [cite: 10]
    Uma Máquina de Estados Finitos (FSM) é um modelo matemático de computação usado para projetar circuitos sequenciais (digitais) e programas de computador. Uma FSM é definida por uma lista de seus estados finitos, suas condições de transição entre esses estados e as ações ou saídas geradas.
    * **Componentes Principais de uma FSM:**
        1.  **Conjunto Finito de Estados (S):** Representa as diferentes condições em que a máquina pode estar. Um dos estados é geralmente designado como estado inicial.
        2.  **Conjunto Finito de Símbolos de Entrada (Alfabeto de Entrada, I):** Define os possíveis valores de entrada que a máquina pode receber.
        3.  **Função de Transição ($\delta$):** Determina o próximo estado da máquina com base no estado atual e na entrada atual. ($\delta$: S x I $\rightarrow$ S)
        4.  **Conjunto Finito de Símbolos de Saída (Alfabeto de Saída, O):** Define os possíveis valores de saída que a máquina pode gerar.
        5.  **Função de Saída ($\lambda$):** Determina a saída da máquina. Existem dois tipos principais:
            * **Máquina de Mealy:** A saída depende do estado atual e da entrada atual ($\lambda$: S x I $\rightarrow$ O).
            * **Máquina de Moore:** A saída depende apenas do estado atual ($\lambda$: S $\rightarrow$ O).
        (Opcionalmente, pode incluir um estado inicial e um conjunto de estados finais ou de aceitação).

7.  **Diagrama de Estados de uma FSM para Detectar "101" (com sobreposição):** [cite: 11]
    Estados:
    * S0: Estado inicial / Nenhum prefixo de "101" detectado.
    * S1: "1" detectado.
    * S2: "10" detectado.
    * S3: "101" detectado (saída = 1).

    Transições (Entrada / Saída):
    * **S0:**
        * Entrada 0 $\rightarrow$ S0 / 0
        * Entrada 1 $\rightarrow$ S1 / 0
    * **S1 (viu "1"):**
        * Entrada 0 $\rightarrow$ S2 / 0 (sequência parcial "10")
        * Entrada 1 $\rightarrow$ S1 / 0 (sequência parcial "1", descarta "1" anterior)
    * **S2 (viu "10"):**
        * Entrada 0 $\rightarrow$ S0 / 0 (sequência "100", quebra "101")
        * Entrada 1 $\rightarrow$ S3 / 1 (sequência "101" detectada!)
    * **S3 (viu "101", saída foi 1):**
        * Entrada 0 $\rightarrow$ S2 / 0 (o último "1" de "101" seguido de "0" forma "10" - sobreposição)
        * Entrada 1 $\rightarrow$ S1 / 0 (o último "1" de "101" seguido de "1" forma "1" - sobreposição)

    (O diagrama de estados mostraria quatro círculos para S0, S1, S2, S3. Setas entre eles seriam rotuladas com "Entrada/Saída". S3 seria o estado onde a saída é '1' quando a transição para ele ocorre devido a uma entrada '1' vinda de S2.)

8.  **Frequência Máxima da Saída de um Flip-Flop JK:** [cite: 12, 13]
    Se um flip-flop JK está configurado para alternar de estado a cada pulso de clock (geralmente com J=1 e K=1), ele atua como um divisor de frequência por 2.
    A frequência do clock é de 50 MHz. [cite: 12]
    Portanto, a frequência máxima da saída será:
    Frequência da Saída = Frequência do Clock / 2
    Frequência da Saída = 50 MHz / 2 = 25 MHz.

9.  **Valor de Q para Flip-Flop Tipo D com Sequência de Entrada:** [cite: 14, 15]
    Flip-flop tipo D acionado na borda de subida do clock. Q inicial = 0.
    Sequência de D: $D=1$ (tempo 0-1), $D=0$ (tempo 1-2), $D=1$ (tempo 2-3), $D=0$ (tempo 3-4).
    Bordas de subida do clock nos instantes t=1, t=2, t=3, t=4.

    * **No instante t=0:** Q = 0 (inicial).
    * **Borda de subida em t=1:** No intervalo [0,1), D=1. Na borda de subida em t=1, o valor de D (que é 1) é capturado.
        * **Q após borda em t=1 torna-se 1.**
    * **Borda de subida em t=2:** No intervalo [1,2), D=0. Na borda de subida em t=2, o valor de D (que é 0) é capturado.
        * **Q após borda em t=2 torna-se 0.**
    * **Borda de subida em t=3:** No intervalo [2,3), D=1. Na borda de subida em t=3, o valor de D (que é 1) é capturado.
        * **Q após borda em t=3 torna-se 1.**
    * **Borda de subida em t=4:** No intervalo [3,4), D=0. Na borda de subida em t=4, o valor de D (que é 0) é capturado.
        * **Q após borda em t=4 torna-se 0.**

    Valores de Q após cada borda:
    * Após t=1: Q = 1
    * Após t=2: Q = 0
    * Após t=3: Q = 1
    * Após t=4: Q = 0

10. **Circuito para Armazenar Valor de Botão Pressionado:** [cite: 16, 17]
    Para armazenar o valor de um botão pressionado (nível alto) até uma reinicialização manual, pode-se usar um flip-flop tipo D.

    * **Componentes:**
        1.  Flip-Flop Tipo D (com entrada D, CLK, Q, e uma entrada de reset assíncrona, por exemplo, Clear ou Reset).
        2.  Botão (que fornece nível alto quando pressionado).
        3.  Sinal de Clock (CLK).
        4.  Um botão ou chave de Reset manual.

    * **Conexões do Circuito:**
        * A saída do botão (que vai para nível alto quando pressionado) é conectada à entrada D do flip-flop.
        * O sinal de Clock é conectado à entrada CLK do flip-flop.
        * A saída Q do flip-flop representa o valor armazenado (indica se o botão foi pressionado).
        * O botão/chave de Reset manual é conectado à entrada de Clear (ou Preset, dependendo da lógica desejada para reinicializar para 0 ou 1) assíncrona do flip-flop. Se for Clear, ele forçará Q para 0 quando ativado.

    * **Diagrama do Circuito:**
        (O diagrama mostraria um flip-flop D. O sinal do "Botão Pressionado" (nível alto) iria para a entrada D. Um sinal de "Clock" iria para a entrada CLK. A saída Q seria a "Indicação de Botão Pressionado". Um sinal de "Reset Manual" iria para a entrada Clear (ou $\overline{CLR}$) do flip-flop.)

    * **Funcionamento:** [cite: 18]
        1.  Inicialmente, assume-se que o flip-flop foi reinicializado, então Q = 0.
        2.  Quando o usuário pressiona o botão, a entrada D do flip-flop vai para nível alto.
        3.  Na próxima borda ativa do sinal de clock (por exemplo, borda de subida), o flip-flop amostra a entrada D. Como D está alta, a saída Q vai para nível alto.
        4.  Uma vez que Q está alto, ele permanecerá alto mesmo que o botão seja solto (fazendo D voltar para baixo), porque o flip-flop tipo D "lembra" o valor que foi capturado na borda do clock.
        5.  A saída Q permanecerá alta, indicando que o botão foi pressionado em algum momento, até que o sistema seja reinicializado manualmente.
        6.  Quando o botão de Reset manual é ativado, a entrada assíncrona Clear (ou similar) do flip-flop é acionada, forçando a saída Q de volta para 0, independentemente do clock ou da entrada D. Isso apaga o valor armazenado.

    * **Nota sobre o Clock:** O clock pode ser um clock contínuo do sistema. Se o botão for pressionado e mantido pressionado por pelo menos um ciclo de clock completo (ou até a próxima borda ativa), seu estado será capturado. Alternativamente, para uma captura mais simples de um evento de botão único, o próprio sinal do botão (após algum condicionamento para evitar *bouncing* e gerar um pulso de clock único) poderia ser usado para gerar o pulso de clock, mas a descrição sugere um "sinal de clock" genérico. A abordagem com clock contínuo e reset assíncrono é mais robusta.