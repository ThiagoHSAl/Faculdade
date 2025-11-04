#ifndef GERENCIADOR_RELATORIOS_HPP
#define GERENCIADOR_RELATORIOS_HPP

#include "lista.hpp"
#include "arvore.hpp"
#include <string>

// Estrutura para o índice auxiliar que liga Pacote -> Clientes
struct NomesClientes {
    std::string remetente;
    std::string destinatario;
};

class GerenciadorRelatorios {
private:
    // Mapeia ID do pacote -> Lista de suas linhas de evento
    ArvoreBuscaBinaria<int, Lista<std::string>*> indicePacotes;
    
    //Mapeia Nome do Cliente -> Lista de IDs de seus pacotes
    ArvoreBuscaBinaria<std::string, Lista<int>*> indiceClientePacotes;

    //Mapeia ID do Pacote -> Nomes do remetente/destinatário
    ArvoreBuscaBinaria<int, NomesClientes*> indicePacoteCliente;

    void processarEvento(const std::string& linha);
    void processarConsultaPacote(const std::string& linha);
    void processarConsultaCliente(const std::string& linha); 

public:
    GerenciadorRelatorios();
    ~GerenciadorRelatorios();

    void processarLinha(const std::string& linha);
};

#endif