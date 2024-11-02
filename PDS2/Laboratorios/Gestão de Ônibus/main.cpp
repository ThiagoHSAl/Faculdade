#include<iostream>
#include <string>
#include <vector>
#include "empresa.hpp"

int main(){
    char comando;
    std::string placa,placa_transferencia;
    int quantidade;//quantidade faz o papel de quantidade maxima no cadasto mas também de quantidade para subir/descer/transferir
    frota minha_frota;
    onibus* meu_onibus;
    onibus* meu_onibus_transferencia=nullptr;  

    while(std::cin>>comando && comando != 'F'){ //de acordo com o comando as entradas são recebidas de forma diferente
       if(comando == 'C'){ //apenas recebe para cadastro, não sendo necessário verificar agora se o onibus existe
            std::cin>>placa>>quantidade;
       }
 
       if(comando == 'S' || comando == 'D'){//recebe apenas uma placa e verifica se o onibus existe
            std::cin>>placa>>quantidade;
            meu_onibus=minha_frota.buscar_onibus(placa,'P');
       }
       
       if(comando == 'T'){//recebe duas placas e verifica se ambas existem
             std::cin>>placa>>placa_transferencia>>quantidade;
             meu_onibus=minha_frota.buscar_onibus(placa,'P');
             if(meu_onibus != nullptr){
                 meu_onibus_transferencia=minha_frota.buscar_onibus(placa_transferencia,'P');
              }
       }
       
       switch(comando){

            case'C':{//constroi um onibus e o adiciona a frota se possível
               onibus bus(placa,quantidade);
               minha_frota.adicionar_onibus(bus);
               break;
            }

            case 'S':{//sobe passageiros se possivel
                if(meu_onibus != nullptr){
                     meu_onibus->subir_passageiros(quantidade);
                }        
                break;
            }
       
            case'D':{//desce passageiros se possivel
                if(meu_onibus != nullptr){
                     meu_onibus->descer_passageiros(quantidade);
                }        
                break;
            }

            case 'T':{//transfere passageiros se possivel
                 if(meu_onibus != nullptr && meu_onibus_transferencia != nullptr){
                     meu_onibus->transferir_passageiros(meu_onibus_transferencia,quantidade);   
                }
                break;
            }

            case 'I':{//imprime a frota na tela
                minha_frota.imprimir_estado();
                break;
            }
        }
       
    }
    return 0;
}
