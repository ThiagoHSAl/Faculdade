#include "aluno.hpp"
#include <iostream>
#include <string>

int main(){
    escola colegio;
    std::string nome;
    int matricula,nota=0;
    std::vector<int> notas;

    while(true){
        std::cin>>nome;
        if(nome == "END"){//recebe o nome de um aluno para cadastro e finaliza com o comando END
            break;
        }
        std::cin>>matricula;
        while(true){//recebe as notas do aluno e finaliza com o comando -1
            std::cin>>nota;
            if(nota == -1){
                break;
            }
            notas.push_back(nota);
        }
        aluno aluno(nome, matricula, notas);//cria um aluno, o adiciona no colegio e reseta o vetor de notas
        colegio.adicionar_aluno(aluno);
        notas.resize(0);
        nota=0;
    }
    colegio.relatorio();//exibe o relatório completo do colégio
    return 0;
}
