#ifndef NOINFODIJKSTRA_HPP
#define NOINFODIJKSTRA_HPP

struct NoInfoDijkstra {
    int idArmazem;
    int distancia;
    int idPredecessor;
    bool visitado;
    NoInfoDijkstra* proximo; 

    NoInfoDijkstra(int id) : idArmazem(id), distancia(-1), idPredecessor(-1), visitado(false), proximo(nullptr) {}
};

class ListaInfoDijkstra {
private:
    NoInfoDijkstra* primeiro;

public:
    ListaInfoDijkstra();
    ~ListaInfoDijkstra();
    void AdicionaInfo(int idArmazem); 
    NoInfoDijkstra* BuscaInfo(int idArmazem); 
    void Reset(); 
};

struct NoHeapDijkstra {
    int idArmazem;
    double distancia;

    NoHeapDijkstra(int id, double dist) : idArmazem(id), distancia(dist) {}

    bool operator>(const NoHeapDijkstra& other) const {
        return this->distancia > other.distancia;
    }
};

#endif