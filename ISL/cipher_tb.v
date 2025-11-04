// Módulo: cipher_tb
// Descrição: Testbench robusto que exibe os resultados em formato BINÁRIO.
`timescale 1ns/1ps

module cipher_tb_robust_binary;

    // Sinais para conectar ao módulo
    reg         clk;
    reg         rst;
    reg         start;
    reg [7:0]   key;
    reg [7:0]   plaintext;
    wire        done;
    wire [7:0]  ciphertext;

    // Variáveis de controle do testbench
    integer     test_count = 0;
    integer     error_count = 0;
    reg [7:0]   expected_ciphertext;

    // Instanciação do Módulo sob Teste (DUT)
    cipher dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .key(key),
        .plaintext(plaintext),
        .done(done),
        .ciphertext(ciphertext)
    );

    // Geração do Clock
    always #5 clk = ~clk; // Clock de 100MHz (período de 10ns)

    // Task para executar um único ciclo de teste e verificar o resultado
    task run_test(input [7:0] test_key, input [7:0] test_plaintext);
    begin
        test_count = test_count + 1;
        $display("----------------------------------------");
        $display("Iniciando Teste %0d", test_count);
        
        key = test_key;
        plaintext = test_plaintext;
        
        start = 1;
        #10;
        start = 0;

        wait(done); 
        
        expected_ciphertext = test_plaintext ^ test_key;
        
        $display("Operação Concluída:");
        $display("  Texto Claro: 8'b%b", test_plaintext);
        $display("  Chave:       8'b%b", test_key);
        $display("  Resultado Esperado:   8'b%b", expected_ciphertext);
        $display("  Resultado Obtido:     8'b%b", ciphertext);
        
        if (ciphertext === expected_ciphertext) begin
            $display(">> Resultado: CORRETO!");
        end else begin
            $display(">> Resultado: INCORRETO!");
            error_count = error_count + 1;
        end
        #20;
    end
    endtask

    // Sequência Principal de Teste
    initial begin
        // --- Inicialização ---
        $dumpfile("cipher_waveform.vcd");
        $dumpvars(0, dut);
        $display("Iniciando simulação robusta...");
        clk = 0;
        rst = 1;
        start = 0;
        key = 8'h00;
        plaintext = 8'h00;
        #20;
        rst = 0;
        $display("Reset liberado.\n");
        #10;

        // --- Casos de Teste Específicos ---
        run_test(8'b10100101, 8'b00111111); // A5, 3F
        run_test(8'b11111111, 8'b11000011); // FF, C3

        // --- Casos de Teste de Borda (Edge Cases) ---
        $display("\n--- Iniciando Testes de Borda ---");
        run_test(8'b00000000, 8'b11001100); // 00, CC
        run_test(8'b01011010, 8'b00000000); // 5A, 00
        run_test(8'b11111111, 8'b10110100); // FF, B4
        run_test(8'b01111110, 8'b01111110); // 7E, 7E

        // --- Testes Aleatórios ---
        $display("\n--- Iniciando Testes Aleatórios ---");
        repeat (5) begin 
            run_test($random, $random);
        end

        // --- Relatório Final ---
        $display("\n----------------------------------------");
        $display("Relatório Final da Simulação:");
        if (error_count == 0) begin
            $display(">> SUCESSO! Todos os %0d testes passaram!", test_count);
        end else begin
            $display(">> FALHA! %0d de %0d testes falharam.", error_count, test_count);
        end
        $display("----------------------------------------");
        
        $finish;
    end

endmodule