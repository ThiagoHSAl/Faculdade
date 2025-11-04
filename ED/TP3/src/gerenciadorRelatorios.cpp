#include "gerenciadorRelatorios.hpp"
#include <sstream>
#include <iostream>
#include <iomanip>

GerenciadorRelatorios::GerenciadorRelatorios() {}

GerenciadorRelatorios::~GerenciadorRelatorios() {
    indicePacotes.limpar();
    indiceClientePacotes.limpar();
    indicePacoteCliente.limpar();
}

void GerenciadorRelatorios::processarLinha(const std::string& linha) {
    if (linha.empty()) return;
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipo;
    ss >> timestamp >> tipo;
    if (tipo == "EV") {
        processarEvento(linha);
    } else if (tipo == "PC") {
        processarConsultaPacote(linha);
    } else if (tipo == "CL") {
        processarConsultaCliente(linha);
    }
}

// Processa um evento, armazenando informações sobre pacotes e clientes.
void GerenciadorRelatorios::processarEvento(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd, tipoEv;
    int idPacote;

    ss >> timestamp >> tipoCmd >> tipoEv >> idPacote;
    Lista<std::string>* relatorioPacote = indicePacotes.busca(idPacote);

    if (relatorioPacote == nullptr) {
        relatorioPacote = new Lista<std::string>();
        indicePacotes.insere(idPacote, relatorioPacote);
    }

    relatorioPacote->insereFinal(linha);
    if (tipoEv == "RG") {
        std::string remetente, destinatario;

        ss >> remetente >> destinatario;
        NomesClientes* nomes = new NomesClientes{remetente, destinatario};
        indicePacoteCliente.insere(idPacote, nomes);
        Lista<int>* pacotesRemetente = indiceClientePacotes.busca(remetente);

        if (pacotesRemetente == nullptr) {
            pacotesRemetente = new Lista<int>();
            indiceClientePacotes.insere(remetente, pacotesRemetente);
        }

        pacotesRemetente->insereFinal(idPacote);
        Lista<int>* pacotesDestinatario = indiceClientePacotes.busca(destinatario);

        if (pacotesDestinatario == nullptr) {
            pacotesDestinatario = new Lista<int>();
            indiceClientePacotes.insere(destinatario, pacotesDestinatario);
        }
        pacotesDestinatario->insereFinal(idPacote);
    }
}

// Processa uma consulta de pacote, imprimindo o histórico de eventos do pacote.
void GerenciadorRelatorios::processarConsultaPacote(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd;
    int idPacote;
    ss >> timestamp >> tipoCmd >> idPacote;

    std::cout << std::setw(6) << std::setfill('0') << timestamp << " " << tipoCmd << " " << std::setw(3) << idPacote << std::endl;
    
    Lista<std::string>* relatorio = indicePacotes.busca(idPacote);

    if (relatorio == nullptr) {
        std::cout << 0 << std::endl;
    } else {
        std::cout << relatorio->getTamanho() << std::endl;
        NoLista<std::string>* atual = relatorio->getPrimeiro();
        while (atual != nullptr) {
            std::cout << atual->dado << std::endl;
            atual = atual->proximo;
        }
    }
}

// Processa uma consulta de cliente, imprimindo o histórico de eventos dos pacotes associados ao cliente.
void GerenciadorRelatorios::processarConsultaCliente(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestampConsulta;
    std::string tipoCmd, nomeCliente;
    ss >> timestampConsulta >> tipoCmd >> nomeCliente;

    std::cout << std::setw(6) << std::setfill('0') << timestampConsulta << " " << tipoCmd << " " << nomeCliente << std::endl;

    Lista<int>* idsPacotes = indiceClientePacotes.busca(nomeCliente);
    if (idsPacotes == nullptr) {
        std::cout << 0 << std::endl;
        return;
    }

    Lista<std::string> linhasResultado;
    NoLista<int>* noIdAtual = idsPacotes->getPrimeiro();

    while (noIdAtual != nullptr) {
        int idPacote = noIdAtual->dado;
        Lista<std::string>* historicoPacote = indicePacotes.busca(idPacote);
        if (historicoPacote != nullptr) {
            std::string linhaRG;
            std::string linhaUltimoEvento;
            long long timestampUltimoEvento = -1;
            
            NoLista<std::string>* noEvento = historicoPacote->getPrimeiro();

            // Percorre os eventos do pacote para encontrar o último evento e o evento RG mais recente.
            while(noEvento != nullptr) {
                std::stringstream ssEvento(noEvento->dado);
                long long timestampEvento;
                std::string cmd, tipoEv;
        
                ssEvento >> timestampEvento >> cmd >> tipoEv;

                if (timestampEvento <= timestampConsulta) {
                    if (tipoEv == "RG") {
                        linhaRG = noEvento->dado;
                    }
                    // usa '>=' para pegar o último evento em caso de timestamps iguais.
                    if (timestampEvento >= timestampUltimoEvento) {
                        timestampUltimoEvento = timestampEvento;
                        linhaUltimoEvento = noEvento->dado;
                    }
                }
                noEvento = noEvento->proximo;
            }

            if (!linhaRG.empty()) {
                linhasResultado.insereOrdenado(linhaRG);
            }
            if (!linhaUltimoEvento.empty() && linhaUltimoEvento != linhaRG) {
                linhasResultado.insereOrdenado(linhaUltimoEvento);
            }
        }
        noIdAtual = noIdAtual->proximo;
    }

    std::cout << linhasResultado.getTamanho() << std::endl;
    NoLista<std::string>* noResultado = linhasResultado.getPrimeiro();
    while(noResultado != nullptr) {
        std::cout << noResultado->dado << std::endl;
        noResultado = noResultado->proximo;
    }
}