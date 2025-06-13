#ifndef NOINFOBFS_HPP
#define NOINFOBFS_HPP

struct NoInfoBFS {
    int idArmazem;
    int distancia;
    int idPredecessor;
    bool visitado;
    NoInfoBFS* proximo; 

    NoInfoBFS(int id) : idArmazem(id), distancia(-1), idPredecessor(-1), visitado(false), proximo(nullptr) {}
};

class ListaInfoBFS {
private:
    NoInfoBFS* primeiro;

public:
    ListaInfoBFS();
    ~ListaInfoBFS();
    void AdicionaInfo(int idArmazem); 
    NoInfoBFS* BuscaInfo(int idArmazem); 
    void Reset(); 
};

#endif