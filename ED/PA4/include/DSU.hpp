#ifndef DSU_HPP
#define DSU_HPP

class DSU {
public:
    DSU(int quantidade_conjuntos);
    ~DSU();

    void Make(int x);
    int Find(int x);
    void Union(int x, int y);

private:
    int tamanho;       
    int* conjuntos;    
    int* rank;         
};

#endif 

