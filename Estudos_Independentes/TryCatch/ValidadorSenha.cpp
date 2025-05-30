#include <iostream>
#include <stdexcept>
#include <string>

// Minhas exceções especializadas
class SenhaMuitoCurtaException : public std::invalid_argument {
public:
    SenhaMuitoCurtaException(const std::string& msg) : std::invalid_argument(msg) {}
};

class SenhaSemMaiusculaException : public std::invalid_argument {
public:
    SenhaSemMaiusculaException(const std::string& msg) : std::invalid_argument(msg) {}
};

class SenhaSemNumeroException : public std::invalid_argument {
public:
    SenhaSemNumeroException(const std::string& msg) : std::invalid_argument(msg) {}
};

bool contemMaiuscula(const std::string& senha) {
    for (auto c : senha) {
        if (std::isupper(static_cast<unsigned char>(c))) {
            return true;
        }
    }
    return false;
}

bool contemNumero(const std::string& senha) {
    for (auto c : senha) {
        if (std::isdigit(static_cast<unsigned char>(c))) {
            return true;
        }
    }
    return false;
}

// Função que lança exceções especializadas
void validarSenha(const std::string& senha) {
    if (senha.length() < 8) {
        throw SenhaMuitoCurtaException("Erro: Senha muito curta");
    } 
    
    else if (!contemMaiuscula(senha)) {
        throw SenhaSemMaiusculaException("Erro: Senha sem letra maiúscula");
    } 
    
    else if (!contemNumero(senha)) {
        throw SenhaSemNumeroException("Erro: Senha sem número");
    }

    else {
        std::cout << "Senha válida!" << std::endl;
    }
}

int main() {
    std::string senha;
    std::cout << "Digite a senha: ";

    while(true){
        std::getline(std::cin, senha);
        try {
            validarSenha(senha);
            std::cout << "Senha validada com sucesso!" << std::endl;
            return 0;
        }
        catch (const SenhaMuitoCurtaException& e) { // Captura EXATAMENTE o tipo de erro
            std::cerr << e.what() << std::endl;
            std::cerr << "ACAO: Criar uma senha com pelo menos 8 caracteres" << std::endl;
        }
        catch (const SenhaSemMaiusculaException& e) {
            std::cerr << e.what() << std::endl;
            std::cerr << "ACAO: Crie uma senha com pelo menos uma letra maiuscula" << std::endl;
        }
        catch (const SenhaSemNumeroException& e) { 
            std::cerr << e.what() << std::endl;
            std::cerr << "ACAO: Crie uma senha com pelo menos um numero." << std::endl;
        }
        catch (const std::invalid_argument& e) { // Captura qualquer outro invalid_argument que não seja os acima
            std::cerr << "Erro (tipo: invalid_argument): " << e.what() << std::endl;
            std::cerr << "ACAO: Erro nao tratado especificamente." << std::endl;
        }
        catch (...) { // Captura qualquer outra exceção que não seja as acima 
            std::cerr << "ACAO: Erro desconhecido" << std::endl;
        }
    }
}