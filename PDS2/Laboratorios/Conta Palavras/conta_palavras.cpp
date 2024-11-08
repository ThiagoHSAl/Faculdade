#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <cctype>

using namespace std;

int main(){
    string filename;

    cin>>filename;
    ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Erro: não foi possível abrir o arquivo!" << std::endl;
        return 1; // Indica erro ao encerrar o programa
    }

    char character;
    string word;
    map <string, int> collection;

    while(file.get(character)){
        if(isalnum(character)){ //qualquer caractere não alfanumérico é considerado um separador
            word+=tolower(character);
        }
        else if(!word.empty()){
            collection[word]++; //utiliza a palavra como chave para um contador no map
            word.clear();
        }
    }

    if(!word.empty()){
        collection[word]++; //pode ser que consuma todos os caracteres sem encontrar um separador não alfanumérico no final do arquivo
        word.clear();
    }

    for(auto &pair : collection){
        cout<<pair.first<<" "<<pair.second<<endl;
    }
    
    file.close();
    return 0;
}
