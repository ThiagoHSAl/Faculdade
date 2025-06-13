#ifndef FILA_IDS_HPP
#define FILA_IDS_HPP

struct FilaNo {
    int id;
    FilaNo* proximo;
    FilaNo(int val) : id(val), proximo(nullptr) {}
};

class FilaIDs {
private:
    FilaNo* primeiro;
    FilaNo* ultimo;
    int tamanho;

public:
    FilaIDs();
    ~FilaIDs();
    void enfileira(int id);
    int desenfileira();
    bool estaVazia() const;
    int getTamanho() const;
};

#endif