CC=g++ 
CFLAGS=-std=c++11 -g 
TARGET=pa3.out
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
$(BIN_DIR)/$(TARGET): $(BUILD_DIR)/Heap.o $(BUILD_DIR)/main.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/Heap.o $(BUILD_DIR)/main.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/main.o: $(INCLUDE_DIR)/Heap.hpp $(SRC_DIR)/main.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

$(BUILD_DIR)/Heap.o: $(INCLUDE_DIR)/Heap.hpp $(SRC_DIR)/Heap.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/Heap.cpp -o $(BUILD_DIR)/Heap.o


# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET)