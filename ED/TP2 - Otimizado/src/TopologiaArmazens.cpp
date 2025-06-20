#include "TopologiaArmazens.hpp"
#include <iostream>
#include <iomanip>
#include <limits>


SecoesArmazem::SecoesArmazem() {
    primeiro = nullptr;
    ultimo = nullptr;
    numeroSecoes = 0;
    idArmazemDono = -1;
}

SecoesArmazem::SecoesArmazem(int idArmazemDono) {
    primeiro = nullptr;
    ultimo = nullptr;
    numeroSecoes = 0;
    this->idArmazemDono = idArmazemDono;
}

SecoesArmazem::~SecoesArmazem(){
    Limpa();
}

TipoCelula* SecoesArmazem::EncontraSecao(int idSecao) const{
    TipoCelula* atual = primeiro;
    while (atual != nullptr) {
        if (atual->pilhaSecao != nullptr) {
            if (atual->pilhaSecao->GetIDEnvio() == idSecao) {
                return atual;
            }
        } 
        atual = atual->proximo;
    }
    return nullptr;
}

PilhaPacotes* SecoesArmazem::InsereSecao(int idSecao, int capacidade, double latencia) {
    TipoCelula* secaoExistente = EncontraSecao(idSecao);
    if (secaoExistente != nullptr) {
        return secaoExistente->pilhaSecao;
    }

    PilhaPacotes* novaPilha = new PilhaPacotes(idSecao);
    TipoCelula* novaCelula = new TipoCelula(novaPilha, capacidade, latencia);

    if (primeiro == nullptr) {
        primeiro = novaCelula;
        ultimo = novaCelula;
    } else {
        ultimo->proximo = novaCelula;
        ultimo = novaCelula;
    }
    numeroSecoes++;
    return novaPilha;
}

PilhaPacotes* SecoesArmazem::GetPilhaSecao(int idSecao) {
    TipoCelula* secao = EncontraSecao(idSecao);
    if (secao != nullptr) {
        return secao->pilhaSecao;
    }
    return nullptr;
}

void SecoesArmazem::Imprime(){
    TipoCelula *impressao = primeiro;
    while(impressao != nullptr){
        if (impressao->pilhaSecao != nullptr) {
            std::cout << "  Secao para Vizinho " << impressao->pilhaSecao->GetIDEnvio()
                      << " (Tamanho: " << impressao->pilhaSecao->getTamanho() << "): ";
            impressao->pilhaSecao->Imprime();
        } else {
            std::cout << "  Secao vazia (sem pilha associada)." << std::endl;
        }
        impressao = impressao -> proximo;
    }
    std::cout<<std::endl;
}


void SecoesArmazem::Limpa(){
    TipoCelula *limpeza;
    TipoCelula *proximoTemporario;

    limpeza = primeiro;
    while(limpeza != nullptr){
        proximoTemporario = limpeza->proximo;
        if (limpeza->pilhaSecao != nullptr) {
            delete limpeza->pilhaSecao;
            limpeza->pilhaSecao = nullptr;
        }
        delete limpeza;          
        limpeza = nullptr; 
        limpeza = proximoTemporario;
    }
    primeiro = nullptr;
    ultimo = nullptr;
    numeroSecoes = 0;
}

int SecoesArmazem::GetNumeroSecoes(){
    return numeroSecoes;
}

TipoCelula* SecoesArmazem::GetPrimeiroCelula() const {
    return primeiro;
}


Armazem::Armazem() {
    secoes = nullptr;
    idArmazem = -1;
}

Armazem::Armazem(int idArmazem) {
    this->idArmazem = idArmazem;
    secoes = new SecoesArmazem(idArmazem);
}

Armazem::~Armazem() {
    delete secoes;
}

void Armazem::ArmazenaPacote(Pacote* pacote, int idPilha) {
    if (secoes != nullptr) {
        PilhaPacotes* pilhaDestino = secoes->GetPilhaSecao(idPilha); 
        if (pilhaDestino != nullptr){
            pilhaDestino->empilhaPacote(pacote); 
        } else {
            std::cerr << "Erro: Secao para o armazem " << idPilha << " nao encontrada no Armazem " << this->idArmazem << std::endl;
        }
    } else {
        std::cerr << "Erro: SecoesArmazem nao inicializadas para o Armazem " << idArmazem << std::endl;
    }
}

int Armazem::GetIdArmazem() const {
    return idArmazem;
}

SecoesArmazem* Armazem::GetSecoes() const {
    return secoes;
}

PilhaPacotes* Armazem::GetDestinoFinal() {
    return &destinoFinal;
}

PilhaPacotes* Armazem::GetSecao(int idSecao) {
    if (secoes == nullptr) {
        return nullptr;
    }

    TipoCelula* currentCelula = secoes->GetPrimeiroCelula(); 
    while (currentCelula != nullptr) {
    
        if (currentCelula->pilhaSecao != nullptr && currentCelula->pilhaSecao->GetIDEnvio() == idSecao) {
            return currentCelula->pilhaSecao;
        }
        currentCelula = currentCelula->proximo;
    }

    return nullptr;
}


TopologiaArmazens::TopologiaArmazens(){
    tamanho = 0;
    primeiroVertice = nullptr;
    ultimoVertice = nullptr;
}


TopologiaArmazens::~TopologiaArmazens() {
    TopologiaArmazensVerticeNo *atual = primeiroVertice;
    while (atual != nullptr) {
        TopologiaArmazensVerticeNo *next = atual->proximo;

        SecoesArmazem* secoes = atual->armazem->GetSecoes();
        if (secoes) {
            TipoCelula* celula = secoes->GetPrimeiroCelula();
            while(celula) {
                if (celula->pilhaSecao) {
                    while(!celula->pilhaSecao->estaVazia()) {
                        delete celula->pilhaSecao->desempilhaPacote();
                    }
                }
                celula = celula->proximo;
            }
        }
        PilhaPacotes* final = atual->armazem->GetDestinoFinal();
        while(final && !final->estaVazia()){
            delete final->desempilhaPacote();
        }

        delete atual->armazem; 
        delete atual;          
        atual = next;
    }
}


TopologiaArmazens::TopologiaArmazens(int numeroVertices, int** matrizCapacidade, double** matrizLatencia) {
    this->tamanho = 0;
    this->primeiroVertice = nullptr;
    this->ultimoVertice = nullptr;

    for (int i = 0; i < numeroVertices; ++i) {
        this->InsereVertice(i);
    }

    for (int i = 0; i < numeroVertices; ++i) {
        for (int j = i + 1; j < numeroVertices; ++j) {
            if (matrizLatencia[i][j] > 0) { 
                int capacidade = matrizCapacidade[i][j];
                double latencia = matrizLatencia[i][j];
                this->InsereAresta(i, j, capacidade, latencia);
            }
        }
    }
}


TopologiaArmazensVerticeNo* TopologiaArmazens::EncontraNoVertice(int idVertice) const{
    TopologiaArmazensVerticeNo *atual = primeiroVertice;
    while (atual != nullptr) {
        if (atual->armazem->GetIdArmazem() == idVertice) {
            return atual;
        }
        atual = atual->proximo;
    }
    return nullptr;
}

Armazem* TopologiaArmazens::GetArmazem(int idArmazem) {
    TopologiaArmazensVerticeNo* no = EncontraNoVertice(idArmazem);
    if (no != nullptr) {
        return no->armazem;
    }
    return nullptr;
}


SecoesArmazem* TopologiaArmazens::GetSecoesArmazem(int idArmazem) {
    TopologiaArmazensVerticeNo* no = EncontraNoVertice(idArmazem);
    if (no != nullptr) {
        return no->secoesAdjacentes;
    }
    return nullptr;
}


Armazem* TopologiaArmazens::InsereVertice(int idArmazem){
    if (EncontraNoVertice(idArmazem) != nullptr) {
        std::cerr << "Erro: Armazem com ID " << idArmazem << " ja existe na TopologiaArmazens." << std::endl;
        return nullptr;
    }

    Armazem* novoArmazem = new Armazem(idArmazem);
    SecoesArmazem *secoesArmazem = novoArmazem->GetSecoes();
    TopologiaArmazensVerticeNo *novo_no = new TopologiaArmazensVerticeNo(novoArmazem, secoesArmazem);

    if (primeiroVertice == nullptr) {
        primeiroVertice = novo_no;
        ultimoVertice = novo_no;
    } else {
        ultimoVertice->proximo = novo_no;
        ultimoVertice = novo_no;
    }
    tamanho++;
    return novoArmazem;
}


void TopologiaArmazens::InsereAresta(int idV, int idW, int capacidade, double latencia) {
    SecoesArmazem *secoesV = GetSecoesArmazem(idV);
    SecoesArmazem *secoesW = GetSecoesArmazem(idW);

    if (secoesV == nullptr || secoesW == nullptr) {
        std::cerr << "Erro: Um ou ambos os armazens da aresta (" << idV << ", " << idW << ") nao existem." << std::endl;
        return;
    }

    secoesV->InsereSecao(idW, capacidade, latencia);
    secoesW->InsereSecao(idV, capacidade, latencia);
}


int TopologiaArmazens::QuantidadeVertices(){
    return tamanho;
}


int TopologiaArmazens::QuantidadeArestas(){
    int arestas = 0;
    TopologiaArmazensVerticeNo *atual = primeiroVertice;
    while (atual != nullptr) {
        arestas += atual->secoesAdjacentes->GetNumeroSecoes();
        atual = atual->proximo;
    }
    return arestas / 2;
}


int TopologiaArmazens::GrauMinimo(){
    if (tamanho == 0) {
        return 0;
    }

    int grauMin = std::numeric_limits<int>::max();
    TopologiaArmazensVerticeNo *atual = primeiroVertice;
    while (atual != nullptr) {
        int grauAtual = atual->secoesAdjacentes->GetNumeroSecoes();
        if (grauAtual < grauMin) {
            grauMin = grauAtual;
        }
        atual = atual->proximo;
    }
    return grauMin;
}


int TopologiaArmazens::GrauMaximo(){
    if (tamanho == 0) {
        return 0;
    }

    int grauMax = 0;
    TopologiaArmazensVerticeNo *atual = primeiroVertice;
    while (atual != nullptr) {
        int grauAtual = atual->secoesAdjacentes->GetNumeroSecoes();
        if (grauAtual > grauMax) {
            grauMax = grauAtual;
        }
        atual = atual->proximo;
    }
    return grauMax;
}


void TopologiaArmazens::ImprimeVizinhos(int idV){
    SecoesArmazem *secoesV = GetSecoesArmazem(idV);
    if (secoesV != nullptr) {
        std::cout << "Secoes de envio/Vizinhos do Armazem " << idV << ":" << std::endl;
        secoesV->Imprime();
    } else {
        std::cout << "Armazem " << idV << " nao encontrado." << std::endl;
    }
}


bool TopologiaArmazens::ExistemSecoesNaoVazias() const {
    TopologiaArmazensVerticeNo* noAtual = primeiroVertice;
    while (noAtual != nullptr) {
        SecoesArmazem* secoes = noAtual->secoesAdjacentes;
        if (secoes != nullptr) {
            TipoCelula* celulaSecaoAtual = secoes->GetPrimeiroCelula();
            while (celulaSecaoAtual != nullptr) {
                PilhaPacotes* pilha = celulaSecaoAtual->pilhaSecao;
                if (pilha != nullptr && !pilha->estaVazia()) {
                    return true;
                }
                celulaSecaoAtual = celulaSecaoAtual->proximo;
            }
        }
        noAtual = noAtual->proximo;
    }
    return false;
}

void TopologiaArmazens::ImprimeEstatisticasFinais() {
    std::cout << "\n--- ESTATISTICAS FINAIS DOS PACOTES ENTREGUES ---" << std::endl;
    
    TopologiaArmazensVerticeNo* v_node = this->primeiroVertice;
    while (v_node != nullptr) {
        PilhaPacotes* pilha_entregues = v_node->armazem->GetDestinoFinal();

        if (pilha_entregues != nullptr && !pilha_entregues->estaVazia()) {
            std::cout << "Armazem de Entrega: " << v_node->armazem->GetIdArmazem() << std::endl;
            
            PilhaPacotes pilha_temp;
            while (!pilha_entregues->estaVazia()) {
                // desempilhaPacote agora retorna Pacote*
                Pacote* pacote = pilha_entregues->desempilhaPacote();
                
                std::cout << "  - Pacote ID: " << std::setw(3) << std::setfill('0') << pacote->getIdUnico()
                          << " | Tempo Armazenado Total: " << std::fixed << std::setprecision(2) << pacote->getTempoArmazenado()
                          << " | Tempo em Transito Total: " << std::fixed << std::setprecision(2) << pacote->getTempoEmTransito()
                          << std::endl;
                
                pilha_temp.empilhaPacote(pacote);
            }

            while (!pilha_temp.estaVazia()) {
                pilha_entregues->empilhaPacote(pilha_temp.desempilhaPacote());
            }
        }
        v_node = v_node->proximo;
    }
    std::cout << "----------------------------------------------------" << std::endl;
}

double TopologiaArmazens::GetLatenciaAresta(int idOrigem, int idDestino) const {
    TopologiaArmazensVerticeNo* noOrigem = this->EncontraNoVertice(idOrigem);
    if (noOrigem) {
        SecoesArmazem* secoes = noOrigem->secoesAdjacentes;
        if (secoes) {
            TipoCelula* celula = secoes->EncontraSecao(idDestino);
            if (celula) {
                return celula->infoAresta.latencia;
            }
        }
    }
    return -1.0;
}

int TopologiaArmazens::GetCapacidadeAresta(int idOrigem, int idDestino) const{
    TopologiaArmazensVerticeNo* noOrigem = this->EncontraNoVertice(idOrigem);
    
    if (noOrigem != nullptr) {
        SecoesArmazem* secoes = noOrigem->secoesAdjacentes;
        if (secoes != nullptr) {
            TipoCelula* celulaSecao = secoes->EncontraSecao(idDestino);
            if (celulaSecao != nullptr) {
                return celulaSecao->infoAresta.capacidade;
            }
        }
    }
    return -1;
}

