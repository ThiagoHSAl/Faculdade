#ifndef HEAPINT_HPP
#define HEAPINT_HPP
#include <iostream>

class HeapInt{
    private : int *inteiro;

    public :
    HeapInt();
    HeapInt(int valor);
    HeapInt(const HeapInt &objeto);
    ~HeapInt();

    //Sobrecarga de operadores
    HeapInt& operator = (int valor);
    HeapInt& operator = (const HeapInt &objeto);
    HeapInt operator + (const HeapInt &objeto);
    HeapInt operator - (const HeapInt &objeto);
    bool operator == (const HeapInt &objeto) const;
    friend std::ostream& operator << (std::ostream &fluxo, HeapInt &objeto);
    friend std::istream& operator >> (std::istream &fluxo, HeapInt &objeto);

};
#endif
 