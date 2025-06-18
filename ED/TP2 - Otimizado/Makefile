CC=g++ 
CFLAGS=-std=c++11 -g 
TARGET=tp2.out
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
$(BIN_DIR)/$(TARGET):$ $(BUILD_DIR)/Planejamento.o $(BUILD_DIR)/ListaEncadeadaRota.o $(BUILD_DIR)/NoInfoDijkstra.o $(BUILD_DIR)/Pacote.o $(BUILD_DIR)/TopologiaArmazens.o $(BUILD_DIR)/Escalonador.o $(BUILD_DIR)/Transporte.o $(BUILD_DIR)/main.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/Planejamento.o $(BUILD_DIR)/ListaEncadeadaRota.o $(BUILD_DIR)/NoInfoDijkstra.o $(BUILD_DIR)/Pacote.o $(BUILD_DIR)/TopologiaArmazens.o $(BUILD_DIR)/Transporte.o $(BUILD_DIR)/Escalonador.o $(BUILD_DIR)/main.o
# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/main.o:  $(INCLUDE_DIR)/Transporte.hpp $(SRC_DIR)/main.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

$(BUILD_DIR)/Transporte.o: $(INCLUDE_DIR)/Planejamento.hpp $(INCLUDE_DIR)/MinHeap.hpp $(INCLUDE_DIR)/Fila.hpp $(INCLUDE_DIR)/NoInfoDijkstra.hpp $(INCLUDE_DIR)/ListaEncadeadaRota.hpp $(INCLUDE_DIR)/Pacote.hpp $(INCLUDE_DIR)/TopologiaArmazens.hpp $(SRC_DIR)/Transporte.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/Transporte.cpp -o $(BUILD_DIR)/Transporte.o

$(BUILD_DIR)/TopologiaArmazens.o :$(SRC_DIR)/TopologiaArmazens.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/TopologiaArmazens.cpp -o $(BUILD_DIR)/TopologiaArmazens.o

$(BUILD_DIR)/Pacote.o: $(INCLUDE_DIR)/Pacote.hpp $(SRC_DIR)/Pacote.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/Pacote.cpp -o $(BUILD_DIR)/Pacote.o
	
$(BUILD_DIR)/NoInfoDijkstra.o: $(INCLUDE_DIR)/NoInfoDijkstra.hpp $(SRC_DIR)/NoInfoDijkstra.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/NoInfoDijkstra.cpp -o $(BUILD_DIR)/NoInfoDijkstra.o
	
$(BUILD_DIR)/ListaEncadeadaRota.o: $(INCLUDE_DIR)/ListaEncadeadaRota.hpp $(SRC_DIR)/ListaEncadeadaRota.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/ListaEncadeadaRota.cpp -o $(BUILD_DIR)/ListaEncadeadaRota.o

$(BUILD_DIR)/Planejamento.o: $(INCLUDE_DIR)/Planejamento.hpp $(SRC_DIR)/Planejamento.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/Planejamento.cpp -o $(BUILD_DIR)/Planejamento.o

$(BUILD_DIR)/Escalonador.o: $(INCLUDE_DIR)/Escalonador.hpp $(INCLUDE_DIR)/MinHeap.hpp $(INCLUDE_DIR)/TopologiaArmazens.hpp $(INCLUDE_DIR)/Transporte.hpp $(INCLUDE_DIR)/Pacote.hpp $(SRC_DIR)/Escalonador.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/Escalonador.cpp -o $(BUILD_DIR)/Escalonador.o

# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET)