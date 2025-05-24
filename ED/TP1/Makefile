CC=g++ 
CFLAGS=-std=c++11 -g 
TARGET=tp1.out
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
$(BIN_DIR)/$(TARGET):$(BUILD_DIR)/AnaliseExperimental.o $(BUILD_DIR)/ValidacaoArquivo.o $(BUILD_DIR)/AlgoritmosOrdenacao.o $(BUILD_DIR)/OrdenadorUniversal.o $(BUILD_DIR)/main.o
	$(CC) $(CFLAGS) -o $(BIN_DIR)/$(TARGET) $(BUILD_DIR)/AnaliseExperimental.o $(BUILD_DIR)/ValidacaoArquivo.o $(BUILD_DIR)/AlgoritmosOrdenacao.o $(BUILD_DIR)/OrdenadorUniversal.o $(BUILD_DIR)/main.o

# Regras para compilar cada arquivo objeto individualmente
$(BUILD_DIR)/main.o:  $(INCLUDE_DIR)/AnaliseExperimental.hpp $(INCLUDE_DIR)/itemT.hpp $(INCLUDE_DIR)/ValidacaoArquivo.hpp $(INCLUDE_DIR)/AlgoritmosOrdenacao.hpp $(INCLUDE_DIR)/OrdenadorUniversal.hpp $(SRC_DIR)/main.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

$(BUILD_DIR)/ValidacaoArquivo.o: $(INCLUDE_DIR)/ValidacaoArquivo.hpp $(SRC_DIR)/ValidacaoArquivo.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/ValidacaoArquivo.cpp -o $(BUILD_DIR)/ValidacaoArquivo.o

$(BUILD_DIR)/AnaliseExperimental.o: $(INCLUDE_DIR)/AnaliseExperimental.hpp $(INCLUDE_DIR)/itemT.hpp $(SRC_DIR)/AnaliseExperimental.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/AnaliseExperimental.cpp -o $(BUILD_DIR)/AnaliseExperimental.o
	
$(BUILD_DIR)/AlgoritmosOrdenacao.o: $(INCLUDE_DIR)/AlgoritmosOrdenacao.hpp $(INCLUDE_DIR)/itemT.hpp $(INCLUDE_DIR)/OrdenadorUniversal.hpp $(SRC_DIR)/AlgoritmosOrdenacao.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/AlgoritmosOrdenacao.cpp -o $(BUILD_DIR)/AlgoritmosOrdenacao.o

$(BUILD_DIR)/OrdenadorUniversal.o: $(INCLUDE_DIR)/OrdenadorUniversal.hpp $(INCLUDE_DIR)/itemT.hpp $(SRC_DIR)/OrdenadorUniversal.cpp
	$(CC) $(CFLAGS) -I $(INCLUDE_DIR) -c $(SRC_DIR)/OrdenadorUniversal.cpp -o $(BUILD_DIR)/OrdenadorUniversal.o
	
# Limpeza dos arquivos gerados
clean:
	rm -f $(BUILD_DIR)/* $(BIN_DIR)/$(TARGET)