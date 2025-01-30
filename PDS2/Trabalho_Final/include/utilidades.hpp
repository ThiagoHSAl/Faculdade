#ifndef UTILIDADES_HPP
#define UTILIDADES_HPP

bool validacao_entrada();
void limpa_tela();
bool validacao_fluxo_linha(std::istringstream &fluxo, std::ofstream &erros, std::string &linha);
void sleep(double i);
bool vazio(std::string &palavra);
bool valida_apelido(std::string &linha, std::string &apelido);
#endif