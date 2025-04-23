#ifndef TIPOCELULA_HPP
#define TIPOCELULA_HPP

class TipoCelula {
    public:
        TipoCelula();
        TipoCelula(int item);

    private:
        int item;
        TipoCelula *proximo;
    
    friend class ListaAdjacencia;
};

#endif