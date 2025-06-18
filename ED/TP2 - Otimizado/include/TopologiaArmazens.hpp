#ifndef TOPOLOGIA_ARMAZENS_HPP
#define TOPOLOGIA_ARMAZENS_HPP

#include "Pacote.hpp"
#include "TipoCelula.hpp"

class SecoesArmazem {
public:
    SecoesArmazem();
    SecoesArmazem(int idArmazemDono);
    ~SecoesArmazem();

    PilhaPacotes* InsereSecao(int idSecao, int capacidade, double latencia); 
    PilhaPacotes* GetPilhaSecao(int idSecao); 
    void Imprime();
    void Limpa();
    int GetNumeroSecoes();
    TipoCelula* GetPrimeiroCelula() const;
    TipoCelula* EncontraSecao(int idSecao);

private:
    TipoCelula* primeiro;
    TipoCelula* ultimo;
    int numeroSecoes;
    int idArmazemDono;

    friend class transporte;
};


class Armazem{
private:
    SecoesArmazem* secoes;
    PilhaPacotes destinoFinal;
    int idArmazem;
    
public:
    Armazem();
    explicit Armazem(int idArmazem);
    ~Armazem();

    void ArmazenaPacote(Pacote& pacote, int idPilha);
    PilhaPacotes* GetSecao(int idSecao);
    int GetIdArmazem() const;
    SecoesArmazem* GetSecoes() const; 
    PilhaPacotes* GetDestinoFinal();
    int getIdSecaoDestino(int idArmazemDestino) const;
    void ChegaPacote(Pacote& pacote, double tempoAtual); 
};

struct TopologiaArmazensVerticeNo {
    Armazem* armazem;
    SecoesArmazem* secoesAdjacentes;
    TopologiaArmazensVerticeNo* proximo;

    TopologiaArmazensVerticeNo(Armazem* arm, SecoesArmazem* secoesPtr)
        : armazem(arm), secoesAdjacentes(secoesPtr), proximo(nullptr) {}
};

class TopologiaArmazens {
public:
    TopologiaArmazens();
    TopologiaArmazens(int numeroVertices, int** matrizCapacidade, double** matrizLatencia); 
    ~TopologiaArmazens();

    Armazem* InsereVertice(int idArmazem);
    void InsereAresta(int idV, int idW, int capacidade, double latencia);

    int QuantidadeVertices();
    int QuantidadeArestas();
    int GrauMinimo();
    int GrauMaximo();
    void ImprimeVizinhos(int idV);
    void ImprimeEstatisticasFinais(); 
    double GetLatenciaAresta(int idOrigem, int idDestino) const;
    int GetCapacidadeAresta(int idOrigem, int idDestino);

    Armazem* GetArmazem(int idArmazem);
    SecoesArmazem* GetSecoesArmazem(int idArmazem);

    bool ExistemSecoesNaoVazias() const;

    TopologiaArmazensVerticeNo* primeiroVertice;

private:
    TopologiaArmazensVerticeNo* ultimoVertice;
    int tamanho;

    TopologiaArmazensVerticeNo* EncontraNoVertice(int idVertice);
};

#endif