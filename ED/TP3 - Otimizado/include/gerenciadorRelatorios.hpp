#ifndef GERENCIADOR_RELATORIOS_HPP
#define GERENCIADOR_RELATORIOS_HPP

#include "lista.hpp"
#include "arvore.hpp"
#include "vetorEventos.hpp" // --- MUDANÇA: Inclui nosso novo vetor
#include <string>

struct NomesClientes {
    std::string remetente;
    std::string destinatario;
};

class GerenciadorRelatorios {
private:
    VetorEventos bancoDeEventos;

    // Índices originais
    ArvoreBuscaBinaria<int, Lista<std::string>*> indicePacotes;
    ArvoreBuscaBinaria<std::string, Lista<int>*> indiceClientePacotes;
    ArvoreBuscaBinaria<int, NomesClientes*> indicePacoteCliente;

    // Índices para Pontos Extra
    ArvoreBuscaBinaria<std::string, Lista<int>*> indiceMovimentosArmazem;
    ArvoreBuscaBinaria<std::string, int*> indiceCongestionamento;
    ArvoreBuscaBinaria<std::string, Lista<int>*> indiceTrajetoria;

    // Métodos de processamento
    void processarEvento(const std::string& linha);
    void processarConsultaPacote(const std::string& linha);
    void processarConsultaCliente(const std::string& linha);
    void processarConsultaMovimento(const std::string& linha);
    void processarConsultaCongestionamento(const std::string& linha);
    void processarConsultaRota(const std::string& linha);

public:
    GerenciadorRelatorios();
    ~GerenciadorRelatorios();

    void processarLinha(const std::string& linha);
};

#endif