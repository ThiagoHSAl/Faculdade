// Módulo: cipher_bonus
// Descrição: Cifrador de BLOCO parametrizado com FSM de 4 estados.

module cipher_bonus #(
    parameter PLAINTEXT_WIDTH = 32,
    parameter KEY_WIDTH       = 8
)(
    input wire                            clk,
    input wire                            rst,
    input wire                            start,
    input wire  [KEY_WIDTH-1:0]           key,
    input wire  [PLAINTEXT_WIDTH-1:0]     plaintext,

    output wire                           done,
    output wire [PLAINTEXT_WIDTH-1:0]     ciphertext
);

    // Calcula a largura necessária para o contador de bits
    localparam COUNTER_WIDTH = $clog2(PLAINTEXT_WIDTH);

    // Definição dos estados da FSM
    parameter IDLE    = 2'b00;
    parameter LOAD    = 2'b01;
    parameter PROCESS = 2'b10;
    parameter DONE    = 2'b11;

    // Sinais internos
    reg [1:0]                       state, next_state;
    reg [COUNTER_WIDTH-1:0]         bit_counter;
    reg [KEY_WIDTH-1:0]             key_reg;
    reg [PLAINTEXT_WIDTH-1:0]       plaintext_reg;
    reg [PLAINTEXT_WIDTH-1:0]       ciphertext_reg;

    // Bloco 1: Lógica de Transição de Estados (Sequencial)
    always @(posedge clk or posedge rst) begin
        if (rst)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Bloco 2: Lógica de Próximo Estado (Combinacional)
    always @(*) begin
        next_state = state;
        case (state)
            IDLE:     if (start) next_state = LOAD;
            LOAD:     next_state = PROCESS;
            PROCESS:  if (bit_counter == PLAINTEXT_WIDTH - 1) next_state = DONE;
            DONE:     if (!start) next_state = IDLE;
        endcase
    end

    // Bloco 3: Datapath (Lógica de processamento dos dados)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            bit_counter <= 0;
            ciphertext_reg <= 0;
        end else begin
            case (state)
                LOAD: begin
                    key_reg <= key;
                    plaintext_reg <= plaintext;
                    ciphertext_reg <= 0;
                    bit_counter <= 0;
                end
                PROCESS: begin
                    // Reutiliza a chave com o operador de módulo (%)
                    ciphertext_reg[bit_counter] <= plaintext_reg[bit_counter] ^ key_reg[bit_counter % KEY_WIDTH];
                    bit_counter <= bit_counter + 1;
                end
            endcase
        end
    end

    // Lógica de Saída
    assign ciphertext = ciphertext_reg;
    assign done = (state == DONE);

endmodule