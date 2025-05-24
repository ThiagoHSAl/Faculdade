#include "ValidacaoArquivo.hpp"

bool lerIntEstrito(std::istringstream& iss, int& valor) {
    std::string token;
    if (!(iss >> token)) return false;

    std::istringstream tokenStream(token);
    char c;
    if (!(tokenStream >> valor) || tokenStream.get(c)) {
        return false;  // Se sobrar algo após o int, é inválido
    }

    return true;
}

bool verificarFormato(const std::string& nomeArquivo) {
    std::ifstream arquivo(nomeArquivo);
    if (!arquivo.is_open()) {
        std::cerr << "Erro ao abrir o arquivo.\n";
        return false;
    }

    int inteiroInicial;
    double d1, d2, d3, d4;
    int tamanhoVetor;

    // Lê todos os dados do arquivo em um único fluxo
    std::stringstream buffer;
    buffer << arquivo.rdbuf();  // Lê tudo do arquivo para o buffer
    std::istringstream iss(buffer.str());

    // Tenta ler 1 int + 4 doubles + 1 int
    if (!lerIntEstrito(iss, inteiroInicial)) {
    std::cerr << "Erro: esperado um inteiro inicial estrito.\n";
    return false;
    }

    if (!(iss >> d1 >> d2 >> d3 >> d4)) {
        std::cerr << "Erro: esperados 4 valores double após o inteiro inicial.\n";
        return false;
    }
    if (!(iss >> tamanhoVetor) || tamanhoVetor < 0) {
        std::cerr << "Erro: esperado inteiro válido para o tamanho do vetor.\n";
        return false;
    }

    // Tenta ler exatamente N inteiros
    for (int i = 0; i < tamanhoVetor; ++i) {
        int val;
        if (!(iss >> val)) {
            std::cerr << "Erro: esperava " << tamanhoVetor << " inteiros, mas encontrou menos.\n";
            return false;
        }
    }

    // Verifica se há valores a mais
    int extra;
    if (iss >> extra) {
        std::cerr << "Erro: arquivo contém dados extras além dos esperados.\n";
        return false;
    }

    return true;
}