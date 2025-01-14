#include<iostream>
#include "HeapInt.hpp"

HeapInt::HeapInt() : inteiro(new int(0)) {}

HeapInt::HeapInt(int valor) : inteiro(new int(valor)) {}

HeapInt::HeapInt(const HeapInt &objeto) : inteiro(new int(*(objeto.inteiro))) {}

HeapInt::~HeapInt(){
    delete this->inteiro;
}

HeapInt& HeapInt::operator=(int valor){
    if (this->inteiro) {
        delete this->inteiro;
    }
    inteiro = new int(valor);
    return *this;
}

HeapInt& HeapInt::operator=(const HeapInt &objeto){
    if(this != &objeto){
        delete this->inteiro;
        inteiro = new int(*(objeto.inteiro));
    }
    return *this;
}

HeapInt HeapInt::operator+(const HeapInt &objeto){
    return HeapInt(*(this->inteiro) + *(objeto.inteiro)); 
}

HeapInt HeapInt::operator-(const HeapInt &objeto){
    return HeapInt(*(this->inteiro) - *(objeto.inteiro)); 
}

bool HeapInt::operator==(const HeapInt &objeto) const{
    return *(this->inteiro) == *(objeto.inteiro);
}

std::istream& operator >> (std::istream &fluxo, HeapInt &objeto){
    int valor;
    fluxo >> valor;
    if (objeto.inteiro) {
        delete objeto.inteiro; // Libera memória apenas se já foi alocada
    }
    objeto.inteiro = new int(valor);
    return fluxo;
}

std::ostream& operator << (std::ostream &fluxo, HeapInt &objeto){
    fluxo << *(objeto.inteiro);
    return fluxo;
}
