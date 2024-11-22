#include "aluno.hpp"
#include <iostream>
#include<iomanip>
#include<algorithm>

aluno::aluno(std::string nome, int matricula, std::vector<int> notas){//construtor do aluno
    this->nome=nome;
    this->matricula=matricula;
    this->notas=notas;
}

void aluno::media(){//calcula a média das notas com 2 casas decimais e imprime na tela
    int i, quantidade_materias;
    double soma_notas;
    quantidade_materias = notas.size();
    if(quantidade_materias == 0){
        std::cout<<"0";
    }
    else{
        for(i=0; i < quantidade_materias; i++){
            soma_notas += notas[i];
        }
        soma_notas /= quantidade_materias;
        std::cout<< std::fixed<< std::setprecision(2)<<soma_notas<<" ";
    }
}

void aluno::min_max(){//printa na tela a maior e a menor nota do aluno
    int notamin=101,notamax=-1;
    size_t quantidade_materias;
    quantidade_materias=notas.size();
    for(size_t i=0; i < quantidade_materias; i++){
        notamin=std::min(notamin, notas[i]);
        notamax=std::max(notamax, notas[i]);
    }
    if(quantidade_materias == 0){
        std::cout<<"0 0"<<std::endl;
    }
    else{
        std::cout<<notamax<<" "<<notamin<<std::endl;
    }
}

void aluno::imprimir_estado(){//imprime nome, matricula, media e nota max/min de um aluno
    std::cout<<this->matricula<<" "<<this->nome<<" ";
    for(size_t i=0; i < notas.size(); i++){
        std::cout<<notas[i]<<" ";
    }
    std::cout<<std::endl;
    aluno::media();
    aluno::min_max();
}

std::string aluno::get_nome(){//utilizada para comparar nomes e os ordenar em ordem alfabética na função relatório
    return this->nome;
}

escola::escola(){//construtor da escola
    colegio.resize(0);
}

void escola::adicionar_aluno(aluno aluno){
    colegio.push_back(aluno);
}

void escola::relatorio(){//ordena a escola por ordem alfabética dos nomes dos alunos
    std::sort(colegio.begin(), colegio.end(), [](aluno a, aluno b){
        return a.get_nome() < b.get_nome();
    });
    for(size_t i=0; i < colegio.size(); i++){//percorre todos os alunos e imprime na tela
        colegio[i].imprimir_estado();
    }
}
