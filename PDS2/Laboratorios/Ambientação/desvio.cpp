 #include <iostream>
 #include <string>
 #include<bits/stdc++.h>
 #include <cmath>
 using namespace std;

float aritmetica(vector<float> numeros, int n){
    int i;
    float media;
    for(i=0;i<n;i++)
        media+=numeros[i];
    media/=n;
    cout<<media<<endl;
    return media;
}
void desvio(float media, vector<float> numeros, int n){
    int i;
    float desvio=0;
    for(i=0;i<n;i++)
        desvio+=(numeros[i]-media)*(numeros[i]-media);
    desvio/=n;
    desvio=sqrt(desvio);
    cout<<desvio;
}
int main() {
    vector<float> numeros;
    float numero,media;
    int n,i;
    cin>>n;
    for(i=0;i<n;i++){
        cin>>numero;
        numeros.push_back(numero);
    }
    cout<<fixed<<setprecision(4);
    media=aritmetica(numeros,n);
    desvio(media,numeros,n);
}
