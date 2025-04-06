CC=gcc 
CFLAGS=-std=c11 -g 
TARGET=pa1.out
SRC_DIR=./src
INCLUDE_DIR=./include
BUILD_DIR=./obj
BIN_DIR=./bin

# Regra principal, compilando o executável a partir dos objetos
all: $(BIN_DIR) $(BUILD_DIR) $(BIN_DIR)/$(TARGET)

# Regras para garantir que os diretórios existam
$(INCLUDE_DIR):
	mkdir -p $(INCLUDE_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Regra para compilar o executável, a partir dos arquivos objetos
$(BIN_DIR)/$(TARGET): $(BUILD_DIR)/main.o 
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/main.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/main.o: $(SRC_DIR)/main.c
	$(CC) $(CFLAGS) -c $(SRC_DIR)/main.c -o $(BUILD_DIR)/main.o

# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET)