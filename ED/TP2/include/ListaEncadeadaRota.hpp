#ifndef LISTA_ENCADEADA_ROTA_HPP
#define LISTA_ENCADEADA_ROTA_HPP

struct RotaNo {
    int idArmazem;
    RotaNo* proximo;
    RotaNo(int id);
};

class ListaEncadeadaRota {
private:
    RotaNo* primeiro;
    RotaNo* ultimo;
    RotaNo* atualNaRota;
    int tamanho;

public:
    ListaEncadeadaRota();
    ~ListaEncadeadaRota();
    void AdicionaArmazem(int id);
    void InsereNoInicio(int id);
    int GetProximoArmazem() const;
    void Avanca();
    bool EstaNoFinal() const;
    int GetTamanho() const;

    ListaEncadeadaRota(const ListaEncadeadaRota& other);
    ListaEncadeadaRota& operator=(const ListaEncadeadaRota& other);

    RotaNo* GetPrimeiroNo() const;
    RotaNo* GetAtualNaRota() const;

    void Imprime() const;
};

#endif