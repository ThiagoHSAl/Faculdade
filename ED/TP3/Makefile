# Compilador e flags
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -g
LDFLAGS =

# Diretórios
SRCDIR = src
INCDIR = include
OBJDIR = obj
BINDIR = bin

# Arquivos
SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(patsubst $(SRCDIR)/%.cpp,$(OBJDIR)/%.o,$(SOURCES))
EXECUTABLE = $(BINDIR)/tp3.out

# Alvo principal
all: $(EXECUTABLE)

# Regra para criar o executável
$(EXECUTABLE): $(OBJECTS)
	@mkdir -p $(BINDIR)
	$(CXX) $(LDFLAGS) -o $@ $^

# Regra para compilar os arquivos objeto
$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	@mkdir -p $(OBJDIR)
	$(CXX) $(CXXFLAGS) -I$(INCDIR) -c $< -o $@

# Alvo para limpar os arquivos gerados
clean:
	rm -rf $(OBJDIR) $(BINDIR)

# Phony targets
.PHONY: all clean