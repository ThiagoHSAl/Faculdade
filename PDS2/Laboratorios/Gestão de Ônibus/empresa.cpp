#include "empresa.hpp"

frota::frota(){//construtor da frota
    quantidade_onibus=0;
    minha_frota.resize(20,nullptr);
}

frota::~frota(){//destrutor da frota
    for(int i=0; i<quantidade_onibus; i++)
    delete minha_frota[i];
}

void frota::adicionar_onibus(onibus adicionar){
    if(buscar_onibus(adicionar.placa,'N')==nullptr){//adiciona um onibus apenas se ele ainda não existe
        minha_frota[quantidade_onibus]=new onibus(adicionar.placa,adicionar.capacidade_max);
        quantidade_onibus++;
        std::cout<<"novo onibus cadastrado"<<std::endl;
    }
    else{
        std::cout<<"ERRO : onibus repetido"<<std::endl;
    }
}

onibus* frota::buscar_onibus(std::string placa,char print){//o cadastro depende de uma busca, mas não deve ser printado, char print serve pra isso
    for(auto busca : minha_frota){
        if(busca != nullptr && busca->placa==placa){
            return busca;
        }
    }
    if(print=='P'){
         std::cout<<"ERRO : onibus inexistente"<<std::endl;
    }
    return nullptr;
}

void frota::imprimir_estado(){//percorre toda a frota imprimindo as informações
    for(auto busca : minha_frota){
       if(busca!=nullptr){
           busca->imprimir_estado();
       }  
    }
}
