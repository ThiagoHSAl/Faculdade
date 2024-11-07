CC=g++
CFLAGS=-std=c++11 -Wall
TARGET=vpl_execution
SRC_DIR=./src
INCLUDE_DIR=./include
BUILD_DIR=./build

# Regra principal, compilando o executável a partir dos objetos
all: ${TARGET}

# Regra para compilar o executável, a partir dos arquivos objetos
${TARGET}: $(BUILD_DIR)/list.o $(BUILD_DIR)/main.o
	$(CC) $(CFLAGS) -o ${TARGET} $(BUILD_DIR)/list.o $(BUILD_DIR)/main.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/list.o: $(INCLUDE_DIR)/list.hpp $(SRC_DIR)/list.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/list.cpp -o $(BUILD_DIR)/list.o

$(BUILD_DIR)/main.o: $(INCLUDE_DIR)/list.hpp $(INCLUDE_DIR)/node.hpp $(SRC_DIR)/main.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

# Regra para limpar arquivos de compilação
clean:
	rm -f $(BUILD_DIR)/* ${TARGET}
