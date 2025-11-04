#include "gerenciadorRelatorios.hpp"
#include <sstream>
#include <iostream>
#include <iomanip>
#include <cstdio> 
#include <cstdlib> 

// --- ESTRUTURA E FUNÇÃO DE COMPARAÇÃO PARA O QSORT (CONSULTA CONGEST) ---
struct RotaCongestionada {
    std::string rota;
    int contagem;
};

int compararRotas(const void* a, const void* b) {
    RotaCongestionada* rotaA = (RotaCongestionada*)a;
    RotaCongestionada* rotaB = (RotaCongestionada*)b;
    // Retorna > 0 se B for maior, < 0 se A for maior, para ordenar em ordem decrescente
    return (rotaB->contagem - rotaA->contagem);
}
// --------------------------------------------------------------------


GerenciadorRelatorios::GerenciadorRelatorios() {
    // O construtor da classe VetorEventos já é chamado aqui.
}

GerenciadorRelatorios::~GerenciadorRelatorios() {
    // Limpa a memória de todas as árvores
    indicePacotes.limpar();
    indiceClientePacotes.limpar();
    indicePacoteCliente.limpar();
    indiceMovimentosArmazem.limpar();
    indiceCongestionamento.limpar();
    indiceTrajetoria.limpar();
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
    } else if (tipo == "MOV") {
        processarConsultaMovimento(linha);
    } else if (tipo == "CONGEST") {
        processarConsultaCongestionamento(linha);
    } else if (tipo == "ROTA") {
        processarConsultaRota(linha);
    }
}

void GerenciadorRelatorios::processarEvento(const std::string& linha) {
    // Adiciona o evento ao nosso banco de dados central e obtém seu índice
    bancoDeEventos.push_back({linha});
    int indiceDoEvento = bancoDeEventos.getTamanho() - 1;

    // Extrai informações básicas do evento para indexação
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd, tipoEv;
    int idPacote;
    ss >> timestamp >> tipoCmd >> tipoEv >> idPacote;

    // --- Lógica para índices originais (PC, CL) ---
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
    
    // --- Lógica para popular os índices extras ---
    ss.clear();
    ss.seekg(0);
    ss >> timestamp >> tipoCmd >> tipoEv; // Reposiciona o stream para reler

    if (tipoEv == "AR" || tipoEv == "RM" || tipoEv == "UR") {
        int idPacoteIgnorado, armazem, secao;
        ss >> idPacoteIgnorado >> armazem >> secao;
        
        char chave[20];
        sprintf(chave, "%04d", armazem); // Chave é o ID do armazém
        Lista<int>* listaMovimentos = indiceMovimentosArmazem.busca(chave);
        if(listaMovimentos == nullptr){
            listaMovimentos = new Lista<int>();
            indiceMovimentosArmazem.insere(chave, listaMovimentos);
        }
        listaMovimentos->insereFinal(indiceDoEvento);

        if (tipoEv == "UR") {
            // Chave é "armazem_secao" para identificar a rota congestionada
            std::string chaveCongest = std::to_string(armazem) + "_" + std::to_string(secao);
            int* contador = indiceCongestionamento.busca(chaveCongest);
            if (contador == nullptr) {
                contador = new int(1);
                indiceCongestionamento.insere(chaveCongest, contador);
            } else {
                (*contador)++;
            }
        }
    } else if (tipoEv == "TR") {
        int idPacoteIgnorado, origem, destino;
        ss >> idPacoteIgnorado >> origem >> destino;
        
        // Indexa para consulta MOV (movimento de SAÍDA do armazém de origem)
        char chaveMov[20];
        sprintf(chaveMov, "%04d", origem);
        Lista<int>* listaMovimentos = indiceMovimentosArmazem.busca(chaveMov);
        if(listaMovimentos == nullptr){
            listaMovimentos = new Lista<int>();
            indiceMovimentosArmazem.insere(chaveMov, listaMovimentos);
        }
        listaMovimentos->insereFinal(indiceDoEvento);

        // Indexa para consulta ROTA
        std::string chaveRota = std::to_string(origem) + "_" + std::to_string(destino);
        Lista<int>* pacotesNaRota = indiceTrajetoria.busca(chaveRota);
        if (pacotesNaRota == nullptr) {
            pacotesNaRota = new Lista<int>();
            indiceTrajetoria.insere(chaveRota, pacotesNaRota);
        }
        pacotesNaRota->insereFinal(idPacote);
    }
}

void GerenciadorRelatorios::processarConsultaPacote(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd;
    int idPacote;
    ss >> timestamp >> tipoCmd >> idPacote;

    std::cout << std::setw(6) << std::setfill('0') << timestamp << " " << tipoCmd << " " << std::setw(3) << std::setfill('0') << idPacote << std::endl;
    
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
            while(noEvento != nullptr) {
                std::stringstream ssEvento(noEvento->dado);
                long long timestampEvento;
                std::string cmd, tipoEv;
        
                ssEvento >> timestampEvento >> cmd >> tipoEv;

                if (timestampEvento <= timestampConsulta) {
                    if (tipoEv == "RG") {
                        linhaRG = noEvento->dado;
                    }
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

void GerenciadorRelatorios::processarConsultaMovimento(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd;
    int idArmazem;
    long long tempoInicio, tempoFim;
    ss >> timestamp >> tipoCmd >> idArmazem >> tempoInicio >> tempoFim;

    std::cout << "CONSULTA MOV: Armazem " << idArmazem << " de " << tempoInicio << " a " << tempoFim << std::endl;

    char chaveArmazem[20];
    sprintf(chaveArmazem, "%04d", idArmazem);

    Lista<int>* indicesEventos = indiceMovimentosArmazem.busca(chaveArmazem);
    if(indicesEventos == nullptr) {
        std::cout << "Total de Movimentos: 0" << std::endl;
        return;
    }

    int contador = 0;
    NoLista<int>* atual = indicesEventos->getPrimeiro();
    while(atual != nullptr){
        int indice = atual->dado;
        long long tempoEvento;
        std::stringstream ssEv(bancoDeEventos[indice].linhaCompleta);
        ssEv >> tempoEvento;

        if(tempoEvento >= tempoInicio && tempoEvento <= tempoFim){
            if(contador == 0) std::cout << "Movimentos encontrados:" << std::endl;
            std::cout << bancoDeEventos[indice].linhaCompleta << std::endl;
            contador++;
        }
        atual = atual->proximo;
    }

    if (contador == 0) {
         std::cout << "Nenhum movimento encontrado no intervalo de tempo especificado." << std::endl;
    }
}

void GerenciadorRelatorios::processarConsultaCongestionamento(const std::string& linha) {
    std::cout << "CONSULTA CONGEST: Rotas mais congestionadas (por eventos 'UR')" << std::endl;
    std::stringstream ss(linha);
    Lista<ParChaveValor<std::string, int*>>* todosPares = indiceCongestionamento.emOrdemColeta();
    int num_rotas = todosPares->getTamanho();

    if (num_rotas == 0) {
        std::cout << "  Nenhum evento de congestionamento ('UR') registrado." << std::endl;
        delete todosPares;
        return;
    }
    
    RotaCongestionada* rotas = new RotaCongestionada[num_rotas];
    
    NoLista<ParChaveValor<std::string, int*>>* atual = todosPares->getPrimeiro();
    for (int i = 0; i < num_rotas; ++i) {
        rotas[i] = {atual->dado.chave, *(atual->dado.valor)};
        atual = atual->proximo;
    }
    
    qsort(rotas, num_rotas, sizeof(RotaCongestionada), compararRotas);
    
    std::cout << "Ranking de Congestionamento:" << std::endl;
    for (int i = 0; i < num_rotas; ++i) {
        std::cout << "  - Rota (Armazem_Secao): " << rotas[i].rota << ", Eventos de Congestionamento: " << rotas[i].contagem << std::endl;
    }

    delete todosPares;
    delete[] rotas;
}

void GerenciadorRelatorios::processarConsultaRota(const std::string& linha) {
    std::stringstream ss(linha);
    long long timestamp;
    std::string tipoCmd;
    int origem, destino;
    ss >> timestamp >> tipoCmd >> origem >> destino;

    std::cout << "CONSULTA ROTA: Pacotes que passaram por " << origem << " -> " << destino << std::endl;

    std::string chaveRota = std::to_string(origem) + "_" + std::to_string(destino);
    Lista<int>* pacotes = indiceTrajetoria.busca(chaveRota);

    if (pacotes == nullptr || pacotes->getTamanho() == 0) {
        std::cout << "Nenhum pacote utilizou esta rota." << std::endl;
    } else {
        std::cout << "Total de pacotes que usaram a rota: " << pacotes->getTamanho() << std::endl;
        NoLista<int>* atual = pacotes->getPrimeiro();
        while (atual != nullptr) {
            std::cout << "  - Pacote ID: " << atual->dado << std::endl;
            atual = atual->proximo;
        }
    }
}