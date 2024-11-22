#ifndef ALUNO_H
#define ALUNO_H
#include <string>
#include <vector>

class aluno{
    private:
    std::string nome;
    int matricula;
    std::vector<int> notas;

    public:
    aluno(std::string nome, int matricula, std::vector<int> notas);
    aluno() : nome(""), matricula(0), notas() {}
    void media();
    void min_max();
    void imprimir_estado();
    std::string get_nome();
};

class escola{
    private:
    std::vector<aluno> colegio;
    
    public:
    escola();
    void adicionar_aluno(aluno aluno);
    void relatorio();

};
#endif

