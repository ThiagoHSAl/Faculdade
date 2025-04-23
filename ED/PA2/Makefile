CC=g++ 
CFLAGS=-std=c++11 -g 
TARGET=pa2.out
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
$(BIN_DIR)/$(TARGET): $(BUILD_DIR)/TipoCelula.o $(BUILD_DIR)/ListaAdjacencia.o $(BUILD_DIR)/graph.o $(BUILD_DIR)/main.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/TipoCelula.o $(BUILD_DIR)/ListaAdjacencia.o $(BUILD_DIR)/graph.o $(BUILD_DIR)/main.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/main.o:  $(INCLUDE_DIR)/TipoCelula.hpp $(INCLUDE_DIR)/ListaAdjacencia.hpp $(INCLUDE_DIR)/graph.hpp $(SRC_DIR)/main.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

$(BUILD_DIR)/graph.o: $(INCLUDE_DIR)/graph.hpp $(SRC_DIR)/graph.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/graph.cpp -o $(BUILD_DIR)/graph.o

$(BUILD_DIR)/ListaAdjacencia.o: $(INCLUDE_DIR)/TipoCelula.hpp $(INCLUDE_DIR)/ListaAdjacencia.hpp $(SRC_DIR)/ListaAdjacencia.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/ListaAdjacencia.cpp -o $(BUILD_DIR)/ListaAdjacencia.o

$(BUILD_DIR)/TipoCelula.o: $(INCLUDE_DIR)/TipoCelula.hpp $(SRC_DIR)/TipoCelula.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/TipoCelula.cpp -o $(BUILD_DIR)/TipoCelula.o

# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET)