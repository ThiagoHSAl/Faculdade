#ifndef VALIDACAOARQUIVO_HPP
#define VALIDACAOARQUIVO_HPP

#include <sstream>
#include <fstream>
#include <iostream>

bool verificarFormato(const std::string& nomeArquivo);

bool lerIntEstrito(std::istringstream& iss, int& valor);

#endif