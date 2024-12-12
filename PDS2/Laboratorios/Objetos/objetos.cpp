#include<iostream>
#include<list>

class objetos{
    private:
    int _id;
    static int quantidade_objetos;

    public:

    objetos(int id) : _id(id){
        quantidade_objetos++;
    }

    ~objetos(){
        quantidade_objetos--;
    }

    static int getQuantidadeObjetos(){
        return quantidade_objetos;
    }

    int getId(){
        return this->_id;
    }

    objetos* getEndereco(){
        return this;
    }
 
};

int objetos::quantidade_objetos = 0;

int main(){
    std::list<objetos*> lista;
    objetos *objeto;
    char comando;
    int id;
    
    do{
        std::cin>>comando;
        switch (comando){

        case 'A':{ //adiciona um objeto com id sequencial no final da lista

            if(lista.empty()){
                id = 1;
            }

            else{
                auto it = lista.back();
                id = it -> getId() + 1;
            }

            objeto = new objetos(id);
            lista.push_back(objeto);
            std::cout<<objeto->getId()<<" "<<objeto->getEndereco()<<std::endl;
            break;
        }

        case 'C':{ //adiciona um objeto com id fornecido (aceitando apenas negativos) no inicio da lista
            std::cin>>id;

            if(id < 0){
                objeto = new objetos(id);
                std::cout<<objeto->getId()<<" "<<objeto->getEndereco()<<std::endl;
                lista.push_front(objeto);
            }

            else{
                std::cout<<"ERRO"<<std::endl;
            }
            break;
        }
            
        case 'R':{//remove e deleta o primeiro objeto da lista
            if(lista.empty()){
                std::cout<<"ERRO"<<std::endl;
            }

            else{
                objeto = lista.front();
                std::cout<<objeto->getId()<<" "<<objeto->getEndereco()<<std::endl;
                lista.pop_front();
                delete objeto;
            }
            break;
        }

        case 'N':{//imprime a quantidade de objetos existente
            std::cout<<objeto->getQuantidadeObjetos()<<std::endl;
            break;
        }

        case 'P':{//imprime as informações do i-ésimo objeto da lista
            size_t i;
            std::cin>>i;

            if(i < 1 || i > lista.size()){
                std::cout<<"ERRO"<<std::endl;
            }

            else{
                auto it = lista.begin();
                std::advance(it,i-1);
                std::cout<<(*it)->getId()<<" "<<(*it)->getEndereco()<<std::endl;
            }
            break;
        }

        case 'L':{//imprime as informações de todos os objetos da lista
            for(auto busca : lista){
                std::cout<<busca->getId()<<" "<<busca->getEndereco()<<std::endl;
            }
            break;
        }

        default:
            break;
        }

    }while(comando != 'E');//encerra o programa com o comando E

    for(auto busca : lista){
        delete busca;
    }
    
    return 0;
}