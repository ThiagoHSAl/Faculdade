// Módulo: cipher_bonus_tb
`timescale 1ns/1ps

module cipher_bonus_tb;

    parameter PLAINTEXT_WIDTH = 32;
    parameter KEY_WIDTH       = 8;

    reg                               clk;
    reg                               rst;
    reg                               start;
    reg [KEY_WIDTH-1:0]               key;
    reg [PLAINTEXT_WIDTH-1:0]         plaintext;
    wire                              done;
    wire [PLAINTEXT_WIDTH-1:0]        ciphertext;

    integer     error_count = 0;
    reg [PLAINTEXT_WIDTH-1:0]         expected_ciphertext;

    cipher_bonus #(
        .PLAINTEXT_WIDTH(PLAINTEXT_WIDTH),
        .KEY_WIDTH(KEY_WIDTH)
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .key(key),
        .plaintext(plaintext),
        .done(done),
        .ciphertext(ciphertext)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("cipher_bonus_waveform.vcd");
        $dumpvars(0, dut);

        $display("Iniciando simulação final e definitiva...");
        clk = 0; rst = 1; start = 0;
        #30;
        rst = 0;
        
        for (integer test_num = 1; test_num <= 5; test_num = test_num + 1) begin
            $display("----------------------------------------");
            $display("Iniciando Teste Aleatório #%0d", test_num);
            
            wait (dut.done === 0);
            @(posedge clk);

            for (integer i = 0; i < KEY_WIDTH; i=i+32) key[i+:32] = $random;
            for (integer i = 0; i < PLAINTEXT_WIDTH; i=i+32) plaintext[i+:32] = $random;
            
            start <= 1;
            @(posedge clk);
            start <= 0;

            wait (dut.done === 1); 
            #1;
            
            for (integer i = 0; i < PLAINTEXT_WIDTH; i = i + 1) begin
                expected_ciphertext[i] = plaintext[i] ^ key[i % KEY_WIDTH];
            end
            
            if (ciphertext === expected_ciphertext) begin
                $display(">> SUCESSO!");
                $display("   Plaintext: %b", plaintext);
                $display("   Chave:     %b", key);
                $display("   Saída:     %b", ciphertext);
            end else begin
                $display(">> ERRO!");
                $display("   Plaintext: %b", plaintext);
                $display("   Chave:     %b", key);
                $display("   Obtido:    %b", ciphertext);
                $display("   Esperado:  %b", expected_ciphertext);
                error_count = error_count + 1;
            end
        end
        
        #50;

        $display("\n----------------------------------------");
        if (error_count == 0) $display(">> FIM: Todos os testes passaram!");
        else $display(">> FIM: %0d testes falharam.", error_count);
        $display("----------------------------------------");
        $finish;
    end

endmodule