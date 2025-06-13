#ifndef PACOTE_HPP
#define PACOTE_HPP
#include <string>

enum EstadoPacote {
    NAO_POSTADO = 0,
    CHEGADA_ESCALONADA = 1,
    ARMAZENADO = 2,
    REMOVIDO = 3,
    ENTREGUE = 4,
};

struct data{
    int dia;
    int mes;
    int ano;
};

class ListaEncadeadaRota;

class Pacote{
private:
    double timestampPostagem;
    data dataPostagem;
    std::string remetente;
    std::string destinatario;
    std::string tipo;
    int armazemOrigem;
    int armazemDestino;

    int idUnico;
    ListaEncadeadaRota* rota;
    EstadoPacote estadoAtual;
    Pacote* proximo;

    double tempoEsperadoEstadia;
    double tempoArmazenado;
    double tempoEmTransito;

    double tempoEntradaArmazemAtual;
    double tempoSaidaArmazemAtual;
    double tempoInicioTransito;
    double tempoFimTransito;

public:
    Pacote();
    Pacote(data dp, std::string rem, std::string dest, int origem, int destino, std::string tp, int id, double timestampPostagem); // Construtor atualizado
    Pacote(const Pacote& other);
    Pacote& operator=(const Pacote& other);
    ~Pacote();

    double getTimestampPostagem() const;
    data getDataPostagem() const;
    std::string getRemetente() const;
    std::string getDestinatario() const;
    std::string getTipo() const;
    int getArmazemOrigem() const;
    int getArmazemDestino() const;
    int getIdUnico() const;
    ListaEncadeadaRota* getRota() const;
    EstadoPacote getEstadoAtual() const;
    Pacote* getProximo() const;
    double getTempoEsperadoEstadia() const;
    double getTempoArmazenado() const;
    double getTempoEmTransito() const;
    double getTempoEntradaArmazemAtual() const;
    double getTempoSaidaArmazemAtual() const;
    double getTempoInicioTransito() const;
    double getTempoFimTransito() const;
    int getProximoArmazemNaRota() const;
    void setTimestampPostagem(double ts);
    void setDataPostagem(data dp);
    void setRemetente(std::string rem);
    void setDestinatario(std::string dest);
    void setTipo(std::string tp);
    void setArmazemOrigem(int origem);
    void setArmazemDestino(int destino);
    void setIdUnico(int id);
    void setRota(ListaEncadeadaRota* r);
    void setEstadoAtual(EstadoPacote estado);
    void setProximo(Pacote* p);
    void setTempoEsperadoEstadia(double tempo);
    void setTempoArmazenado(double tempo);
    void setTempoEmTransito(double tempo);
    void setTempoEntradaArmazemAtual(double tempo);
    void setTempoSaidaArmazemAtual(double tempo);
    void setTempoInicioTransito(double tempo);
    void setTempoFimTransito(double tempo);

    void avancaNaRota();
    bool chegouAoDestinoFinal() const;
    void ImprimeRota() const;
};

class PilhaPacotes {
    private:
        Pacote* primeiro;
        Pacote* ultimo;
        int tamanho;
        int IDEnvio;

    public:
        PilhaPacotes();
        explicit PilhaPacotes(int idEnvio);
        ~PilhaPacotes();

        void empilhaPacote(Pacote pacote);
        Pacote desempilhaPacote();
        void limpa();
        int getTamanho();
        bool estaVazia();
        int GetIDEnvio() const;
        void Imprime();

        friend class SecoesArmazem;
};

#endif