#include "set.hpp"
#include <iostream>

StringSet::StringSet(int tamanho) {
    tamanhoOriginal = tamanho;
    tamanhoTabela = tamanho;
    tamanhoConjunto = 0;
    tabela = new ElementoTabela[tamanhoTabela];
    for (int i = 0; i < tamanhoTabela; i++) {
        tabela[i].vazio = true;
        tabela[i].retirada = false;
    }
}

StringSet::~StringSet() {
    delete[] tabela;
}

int StringSet::Hash(string s) {
    long long hashVal = 0;
    for (char c : s) {
        hashVal = (hashVal * 31 + c) % tamanhoTabela;
    }
    return static_cast<int>(hashVal);
}

void StringSet::Resize(size_t novoTamanho) {
    ElementoTabela* antigaTabela = tabela;
    int antigoTamanho = tamanhoTabela;

    tamanhoTabela = novoTamanho;
    tabela = new ElementoTabela[tamanhoTabela];
    tamanhoConjunto = 0;

    for (int i = 0; i < tamanhoTabela; i++) {
        tabela[i].vazio = true;
        tabela[i].retirada = false;
    }

    for (int i = 0; i < antigoTamanho; i++) {
        if (!antigaTabela[i].vazio && !antigaTabela[i].retirada) {
            Inserir(antigaTabela[i].dado);
        }
    }
    delete[] antigaTabela;
}

void StringSet::Rehash(int pos) {
}

void StringSet::Inserir(string s) {
    if (tamanhoConjunto >= tamanhoTabela * 0.7) {
        Resize(tamanhoTabela * 2);
    }

    int hashIndex = Hash(s);
    int originalHashIndex = hashIndex;
    
    while (!tabela[hashIndex].vazio && tabela[hashIndex].dado != s) {
        hashIndex = (hashIndex + 1) % tamanhoTabela;
        if (hashIndex == originalHashIndex) {
            return;
        }
    }

    if (tabela[hashIndex].vazio || tabela[hashIndex].retirada) {
        tabela[hashIndex].dado = s;
        tabela[hashIndex].vazio = false;
        tabela[hashIndex].retirada = false;
        tamanhoConjunto++;
    }
}

void StringSet::Remover(string s) {
    int hashIndex = Hash(s);
    int originalHashIndex = hashIndex;

    while (!tabela[hashIndex].vazio || tabela[hashIndex].retirada) {
        if (!tabela[hashIndex].vazio && !tabela[hashIndex].retirada && tabela[hashIndex].dado == s) {
            tabela[hashIndex].retirada = true;
            tabela[hashIndex].vazio = true;
            tamanhoConjunto--;
            return;
        }
        hashIndex = (hashIndex + 1) % tamanhoTabela;
        if (hashIndex == originalHashIndex) {
            break;
        }
    }
}

bool StringSet::Pertence(string s) {
    int hashIndex = Hash(s);
    int originalHashIndex = hashIndex;

    while (!tabela[hashIndex].vazio || tabela[hashIndex].retirada) {
        if (!tabela[hashIndex].vazio && !tabela[hashIndex].retirada && tabela[hashIndex].dado == s) {
            return true;
        }
        hashIndex = (hashIndex + 1) % tamanhoTabela;
        if (hashIndex == originalHashIndex) {
            break;
        }
    }
    return false;
}

StringSet* StringSet::Uniao(StringSet* S) {
    StringSet* uniaoSet = new StringSet(this->tamanhoConjunto + S->tamanhoConjunto + 1);
    
    for (int i = 0; i < this->tamanhoTabela; i++) {
        if (!this->tabela[i].vazio && !this->tabela[i].retirada) {
            uniaoSet->Inserir(this->tabela[i].dado);
        }
    }

    for (int i = 0; i < S->tamanhoTabela; i++) {
        if (!S->tabela[i].vazio && !S->tabela[i].retirada) {
            uniaoSet->Inserir(S->tabela[i].dado);
        }
    }
    return uniaoSet;
}

StringSet* StringSet::Intersecao(StringSet* S) {
    StringSet* intersecaoSet = new StringSet((this->tamanhoConjunto < S->tamanhoConjunto ? this->tamanhoConjunto : S->tamanhoConjunto) + 1);

    for (int i = 0; i < this->tamanhoTabela; i++) {
        if (!this->tabela[i].vazio && !this->tabela[i].retirada) {
            if (S->Pertence(this->tabela[i].dado)) {
                intersecaoSet->Inserir(this->tabela[i].dado);
            }
        }
    }
    return intersecaoSet;
}

StringSet* StringSet::DiferencaSimetrica(StringSet* S) {
    StringSet* diferencaSimetricaSet = new StringSet(this->tamanhoConjunto + S->tamanhoConjunto + 1);

    for (int i = 0; i < this->tamanhoTabela; i++) {
        if (!this->tabela[i].vazio && !this->tabela[i].retirada) {
            if (!S->Pertence(this->tabela[i].dado)) {
                diferencaSimetricaSet->Inserir(this->tabela[i].dado);
            }
        }
    }

    for (int i = 0; i < S->tamanhoTabela; i++) {
        if (!S->tabela[i].vazio && !S->tabela[i].retirada) {
            if (!this->Pertence(S->tabela[i].dado)) {
                diferencaSimetricaSet->Inserir(S->tabela[i].dado);
            }
        }
    }
    return diferencaSimetricaSet;
}

void StringSet::Imprimir() {
    int count = 0;
    for (int i = 0; i < tamanhoTabela; i++) {
        if (!tabela[i].vazio && !tabela[i].retirada) {
            count++;
        }
    }

    string* elements = new string[count];
    int current = 0;
    for (int i = 0; i < tamanhoTabela; i++) {
        if (!tabela[i].vazio && !tabela[i].retirada) {
            elements[current++] = tabela[i].dado;
        }
    }

    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (elements[j] > elements[j + 1]) {
                string temp = elements[j];
                elements[j] = elements[j + 1];
                elements[j + 1] = temp;
            }
        }
    }

    bool first = true;
    cout << "{";
    for (int i = 0; i < count; i++) {
        if (!first) {
            cout << ", ";
        }
        cout << elements[i];
        first = false;
    }
    cout << "}\n";

    delete[] elements;
}