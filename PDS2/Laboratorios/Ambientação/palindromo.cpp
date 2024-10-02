#include <iostream>
 #include <string>
 using namespace std;

int main() {
    string entrada;
    int tamanho;
    getline(cin,entrada);
    tamanho=entrada.length();
    if(tamanho%2==0){
        int i,j=1;
        tamanho/=2;
        tamanho--;
        for(i=0;i<=tamanho;i++){
            if(entrada[tamanho-i]!=entrada[tamanho+j]){
                cout<<"NAO";
                return 0;
            }
           j++;
        }
        cout<<"SIM";
    }
    else {
         int i,j=2;
         tamanho/=2;
         tamanho--;
        for(i=0;i<=tamanho;i++){
            if(entrada[tamanho-i]!=entrada[tamanho+j]){
                cout<<"NAO";
                return 0;
            }
           j++;
        }
        cout<<"SIM";
    }
    return 0;
}
