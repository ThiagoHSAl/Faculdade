CC=g++ 
CFLAGS=-std=c++11 -g -I $(INCLUDE_DIR) -I ./extern/doctest
TARGET=login
SRC_DIR=./src
TESTS_DIR=./tests
INCLUDE_DIR=./include
BUILD_DIR=./obj
BIN_DIR=./bin

# Regra principal, compilando o executável a partir dos objetos
all: $(BIN_DIR) $(BUILD_DIR) $(BIN_DIR)/$(TARGET)

# Regras para garantir que os diretórios existam
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Regra para compilar o executável, a partir dos arquivos objetos
$(BIN_DIR)/$(TARGET): $(BUILD_DIR)/cadastro.o $(BUILD_DIR)/jogador.o $(BUILD_DIR)/login.o $(BUILD_DIR)/board.o $(BUILD_DIR)/tictactoe.o $(BUILD_DIR)/reversi.o $(BUILD_DIR)/modulo_cadastro.o $(BUILD_DIR)/modulo_jogos.o $(BUILD_DIR)/utilidades.o $(BUILD_DIR)/lig4.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/cadastro.o $(BUILD_DIR)/jogador.o $(BUILD_DIR)/login.o $(BUILD_DIR)/board.o $(BUILD_DIR)/tictactoe.o $(BUILD_DIR)/reversi.o $(BUILD_DIR)/modulo_cadastro.o $(BUILD_DIR)/modulo_jogos.o $(BUILD_DIR)/utilidades.o $(BUILD_DIR)/lig4.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/cadastro.o: $(INCLUDE_DIR)/cadastro.hpp $(SRC_DIR)/cadastro.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/cadastro.cpp -o $(BUILD_DIR)/cadastro.o

$(BUILD_DIR)/jogador.o: $(INCLUDE_DIR)/jogador.hpp $(SRC_DIR)/jogador.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/jogador.cpp -o $(BUILD_DIR)/jogador.o

# Mudança: Agora o login.cpp está no src
$(BUILD_DIR)/login.o: $(INCLUDE_DIR)/cadastro.hpp $(INCLUDE_DIR)/jogador.hpp $(SRC_DIR)/login.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/login.cpp -o $(BUILD_DIR)/login.o

$(BUILD_DIR)/board.o: $(INCLUDE_DIR)/board.hpp $(SRC_DIR)/board.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/board.cpp -o $(BUILD_DIR)/board.o

$(BUILD_DIR)/tictactoe.o: $(INCLUDE_DIR)/tictactoe.hpp $(SRC_DIR)/tictactoe.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/tictactoe.cpp -o $(BUILD_DIR)/tictactoe.o

$(BUILD_DIR)/reversi.o: $(INCLUDE_DIR)/reversi.hpp $(SRC_DIR)/reversi.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/reversi.cpp -o $(BUILD_DIR)/reversi.o

$(BUILD_DIR)/lig4.o: $(INCLUDE_DIR)/lig4.hpp $(SRC_DIR)/lig4.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/lig4.cpp -o $(BUILD_DIR)/lig4.o

$(BUILD_DIR)/modulo_cadastro.o: $(INCLUDE_DIR)/modulo_cadastro.hpp $(SRC_DIR)/modulo_cadastro.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/modulo_cadastro.cpp -o $(BUILD_DIR)/modulo_cadastro.o

$(BUILD_DIR)/modulo_jogos.o: $(INCLUDE_DIR)/modulo_jogos.hpp $(SRC_DIR)/modulo_jogos.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/modulo_jogos.cpp -o $(BUILD_DIR)/modulo_jogos.o

$(BUILD_DIR)/utilidades.o: $(INCLUDE_DIR)/utilidades.hpp $(SRC_DIR)/utilidades.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/utilidades.cpp -o $(BUILD_DIR)/utilidades.o

# Adiciona uma regra para compilar o arquivo de tests (tests.cpp)
$(BUILD_DIR)/tests.o: $(INCLUDE_DIR)/board.hpp $(TESTS_DIR)/tests.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -I ./external/doctest -c $(TESTS_DIR)/tests.cpp -o $(BUILD_DIR)/tests.o


# Regra para compilar o executável de tests
$(BIN_DIR)/tests: $(BUILD_DIR)/tests.o $(BUILD_DIR)/cadastro.o $(BUILD_DIR)/jogador.o $(BUILD_DIR)/board.o $(BUILD_DIR)/tictactoe.o $(BUILD_DIR)/reversi.o $(BUILD_DIR)/modulo_cadastro.o $(BUILD_DIR)/modulo_jogos.o $(BUILD_DIR)/utilidades.o $(BUILD_DIR)/lig4.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/tests $(BUILD_DIR)/tests.o $(BUILD_DIR)/cadastro.o $(BUILD_DIR)/jogador.o $(BUILD_DIR)/board.o $(BUILD_DIR)/tictactoe.o $(BUILD_DIR)/reversi.o $(BUILD_DIR)/modulo_cadastro.o $(BUILD_DIR)/modulo_jogos.o $(BUILD_DIR)/utilidades.o $(BUILD_DIR)/lig4.o

# Regra para rodar os tests
test: $(BIN_DIR)/tests
	./$(BIN_DIR)/tests  # Roda o executável de tests

# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET) $(BIN_DIR)/tests
