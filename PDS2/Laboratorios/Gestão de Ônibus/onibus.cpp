#include "onibus.hpp"
#include <iostream>

onibus::onibus(std::string placa, int capacidade_max){//construtor do onibus
    this->placa=placa;
    this->capacidade_max=capacidade_max;
    this->lotacao=0;
}

void onibus::subir_passageiros(int subir){//verifica se é possível subir passageiros e imprime na tela
    if(lotacao + subir <= capacidade_max){
        lotacao+=subir;
        std::cout<<"passageiros subiram com sucesso"<<std::endl;
    }
    else{
        std::cout<<"ERRO : onibus lotado"<<std::endl;
    }     
}

void onibus::descer_passageiros(int descer){//verifica se é possível descer passageiros e imprime na tela
    if(lotacao - descer >= 0){
        lotacao-=descer;
        std::cout<<"passageiros desceram com sucesso"<<std::endl;
    }
    else{
        std::cout<<"ERRO : faltam passageiros"<<std::endl;
    }    
}

void onibus::transferir_passageiros(onibus *receptor, int transferir){//verifica se é possível transferir passageiros e imprime na tela
    if((lotacao - transferir >=0) && (receptor->lotacao + transferir <= receptor->capacidade_max)){
        lotacao-=transferir;
        receptor->lotacao+=transferir;
        std::cout<<"transferencia de passageiros efetuada"<<std::endl; 
    }
    else{
        std::cout<<"ERRO : transferencia cancelada"<<std::endl;
    }   
}

void onibus::imprimir_estado(){//imprime as informações de um ônibus
    std::cout<<placa<<" ("<<lotacao<<"/"<<capacidade_max<<")"<<std::endl;
}
