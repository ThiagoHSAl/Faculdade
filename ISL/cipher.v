// Módulo: cipher
// Descrição: Implementa uma cifra XOR sequencial de 8 bits.

module cipher(
    // Entradas
    input wire          clk,
    input wire          rst,
    input wire          start,
    input wire  [7:0]   key,
    input wire  [7:0]   plaintext,

    // Saídas
    output wire         done,
    output wire [7:0]   ciphertext
);

    // Definição dos estados da FSM
    parameter IDLE    = 2'b00;
    parameter LOAD    = 2'b01;
    parameter PROCESS = 2'b10;
    parameter DONE    = 2'b11;

    // Sinais internos
    reg [1:0]   state, next_state;
    reg [2:0]   bit_counter;
    reg [7:0]   key_reg;
    reg [7:0]   plaintext_reg;
    reg [7:0]   ciphertext_reg;

    // Bloco 1: Lógica de Transição de Estados (Sequencial)
    // Responsável apenas por atualizar o estado atual no pulso de clock.
    always @(posedge clk or posedge rst) begin
        if (rst)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Bloco 2: Lógica de Próximo Estado (Combinacional)
    // Define qual será o próximo estado baseado no estado atual e nas entradas.
    always @(*) begin
        next_state = state;
        case (state)
            IDLE: begin
                if (start)
                    next_state = LOAD;
            end
            LOAD: begin
                next_state = PROCESS;
            end
            PROCESS: begin
                if (bit_counter == 3'd7) 
                    next_state = DONE;
            end
            DONE: begin
                if (!start) 
                    next_state = IDLE;
            end
        endcase
    end

    // Bloco 3: Lógica de Saída e Datapath (Sequencial)
    // Gerencia os registradores, o contador e as saídas.
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            bit_counter <= 3'b0;
            ciphertext_reg <= 8'b0;
        end else begin
            case (state)
                LOAD: begin
                    key_reg <= key;
                    plaintext_reg <= plaintext;
                    ciphertext_reg <= 8'b0; 
                    bit_counter <= 3'b0;    
                end
                PROCESS: begin
                    // Executa o XOR para o bit atual e incrementa o contador
                    ciphertext_reg[bit_counter] <= plaintext_reg[bit_counter] ^ key_reg[bit_counter];
                    bit_counter <= bit_counter + 1;
                end
            endcase
        end
    end

    // Atribuições de saída contínuas
    assign ciphertext = ciphertext_reg;
    assign done = (state == DONE);

endmodule