#include <iostream>
#include "cadastro.hpp"
#include "utilidades.hpp"
#include <string>
#include <sstream>


void menu(){
    limpa_tela();
    std::cout<< "Digite:" <<std::endl;
    std::cout<< "C -> Cadastrar usuário" <<std::endl;
    std::cout<< "E -> Editar usuário" <<std::endl;
    std::cout<< "D -> Deletar usuário" <<std::endl;
    std::cout<< "I -> Imprimir usuários" <<std::endl;
    std::cout<< "R -> Exibir o Ranking" <<std::endl;
    std::cout<< "M -> Voltar para o menu inicial" <<std::endl;
    std::cout<< "F -> Finalizar" <<std::endl;
}


int modulo_cadastro(cadastro &meucadastro){
    std::string linha;
    char comando;
    menu();
    while(std::cin >> linha){
        std::string nome, apelido, novoapelido;
        std::istringstream input(linha);
        input.get(comando);
        limpa_tela();
        switch (tolower(comando))
        {
        
        //Cadastro de jogador
        case 'c':{
            getchar();
            std::cout << "Digite o nome:" << std::endl;
            getline(std::cin, nome);
            if(!vazio(nome)){//Evita nomes vazios
                break;
            }
            std::cout << "Digite o apelido (apenas uma palavra permitida)" << std::endl;
            getline(std::cin, linha);
            if(!valida_apelido(linha,apelido)){
                break;
            }
            meucadastro.CadastraJogador(nome,apelido);
            break;
        }


        //Edição de jogador
        case 'e':{
            getchar();
            std::cout << "Apelidos disponiveis para edicao" << std::endl;
            meucadastro.ExibeApelidos();
            std::cout << "Digite o apelido para edicao (apenas uma palavra permitida)" << std::endl;
            getline(std::cin, linha);
            if(!valida_apelido(linha,apelido)){//evita apelidos vazios e com mais de uma palavra
                break;
            }
            if(meucadastro.VerificaApelido(apelido) == -1){ //Verifica se o apelido está cadastrado
                std::cout << "Erro apelido inexistente" << std::endl;
                sleep(2);
                break;
            }
            std::cout << "Digite o novo apelido (apenas uma palavra permitida)" << std::endl;
            getline(std::cin, linha);
            if(!valida_apelido(linha,novoapelido)){
                break;
            }
            meucadastro.EditaJogador(apelido,novoapelido);
            break;
        }


        //Deletor de jogadores
        case 'd':{
            getchar();
            std::cout << "Apelidos existentes" << std::endl;
            meucadastro.ExibeApelidos();
            std::cout << "Digite o apelido para deletar (apenas uma palavra permitida)" << std::endl;
            getline(std::cin, linha);
            if(!valida_apelido(linha,apelido)){//Evita apelidos com mais de uma palavra e apelidos vazios
                break;
            }
            meucadastro.DeletaJogador(apelido);
            break;
        }

        case 'i':{
            limpa_tela();
            meucadastro.Imprime();
            std::cout << "Aperte Enter para voltar" << std::endl;
            getchar();
            std::cin.get();
            break;
        }


        //Retorna 1 para o menu anterior, que mantém o programa funcionando
        case 'm':{
            return 1;
        }


        //Retorna 3 pra o menu anterior, que finaliza o programa
        case 'f':{
            return 3;
        }

        case 'r':{
            meucadastro.Ranking();
            break;
        }

        default:{
            std::cout<< "Erro: comando não existente" <<std::endl;
            sleep(2);
            break;
        }
        }
        menu();
    }
    return 3;
}