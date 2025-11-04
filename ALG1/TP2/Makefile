# --- Compilador e Flags ---
CC=g++

# Flags de aviso exigidas
WARNING_FLAGS = -Wall -Wextra -Wpedantic -Wformat-security -Wconversion -Werror

# Flags de compilação gerais (padrão C++14, debug, e os avisos)
CFLAGS = -std=c++14 -g $(WARNING_FLAGS)

# --- Diretórios e Arquivos ---
TARGET=tp2.out
SRC_DIR=src
INCLUDE_DIR=include
BUILD_DIR=obj

# Flags para o pré-processador: informa onde encontrar os arquivos de cabeçalho (.hpp)
CPPFLAGS = -I$(INCLUDE_DIR)

# Encontra automaticamente TODOS os arquivos .cpp dentro da pasta src
SRCS = $(wildcard $(SRC_DIR)/*.cpp)

# Gera automaticamente os nomes dos arquivos objeto (.o) a partir dos arquivos fonte (.cpp)
OBJS = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(SRCS))

# --- Regras do Makefile ---

# A primeira regra é a padrão. 'all' é um nome comum para a regra principal.
all: $(TARGET)

# Regra para LINKAR o executável final a partir dos arquivos objeto.
$(TARGET): $(OBJS) 
	@echo "Ligando o executável: $@"
	$(CC) $(CFLAGS) -o $@ $^

# Regra PADRÃO para COMPILAR qualquer arquivo .cpp de 'src' para um .o em 'obj'.
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	@echo "Compilando $<..."
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

# Regra para criar os diretórios de saída, caso não existam.
$(BUILD_DIR):
	mkdir -p $@

# Regra "clean" para apagar os arquivos gerados (executada com 'make clean')
clean:
	@echo "Limpando arquivos compilados..."
	rm -rf $(BUILD_DIR) $(TARGET)

# Declara que 'all' e 'clean' não são nomes de arquivos reais, mas sim "alvos falsos".
.PHONY: all clean