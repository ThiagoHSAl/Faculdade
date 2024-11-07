// Você *NÃO* deve alterar esse arquivo

#include <iostream>
#include <string>

#include "list.hpp"

using namespace std;

int main() {
    List lista;

    // Le o numero de elementos
    int n;
    cin >> n;

    // insere os elementos de 1 a n na lista
    for (int i = 1; i <= n; i++)
        lista.insertNode(i);

    lista.display();

    // armazena os endereços dos nós para verificação da inversão
    Node **nodeAddr = new Node *[n];
    Node *p = lista.head;
    for (int i = 0; i < n; i++) {
        nodeAddr[i] = p;
        p = p->next;
    }

    lista.inverte();

    lista.display();

    // verifica inversão comparando os endereços salvos e os atuais
    bool ok = true;
    p = lista.head;
    for (int i = n - 1; i >= 0; i--) {
        if (nodeAddr[i] != p) {
            ok = false;
            break;
        }
        p = p->next;
    }
    cout << (ok ? "SIM" : "NAO") << endl;

    return 0;
}
