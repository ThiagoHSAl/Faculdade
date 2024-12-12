#include<iostream>
#include<cmath>
#include<vector>
#include<iomanip>


class Ponto{ //classe utilizada como objeto para o centro das figuras geometricas

    private:
    int _x;
    int _y;

    public:
    Ponto(int x, int y) : _x(x), _y(y){}

    int getX(){
        return this->_x;
    }

    int getY(){
        return this->_y;
    }
};


class FiguraGeometrica{ //Classe base virtual para as figuras geometricas

    protected:
    Ponto centro;

    public:
    FiguraGeometrica(int x, int y) : centro(x,y) {}
    virtual ~FiguraGeometrica() {}

    virtual void Desenha(){
        std::cout << this->centro.getX() << " " << this->centro.getY() << " ";
    }

    virtual float CalculaArea() = 0;
};


class Retangulo : public FiguraGeometrica{//subclasse retangulo

    private:
    int _lado1;
    int _lado2;

    public:
    Retangulo(int x, int y, int lado1, int lado2) : FiguraGeometrica(x,y), _lado1(lado1), _lado2(lado2){}

    void Desenha() override{
        FiguraGeometrica::Desenha();
        std::cout << "RETANGULO" << std::endl;
    }

    float CalculaArea() override{
        return _lado1*_lado2;
    }
};

class Circulo : public FiguraGeometrica{//subclasse circulo

    private:
    int _raio;

    public:
    Circulo(int x, int y, int raio) : FiguraGeometrica(x,y), _raio(raio){}

    void Desenha() override{
        FiguraGeometrica::Desenha();
        std::cout << "CIRCULO" << std::endl;
    }

    float CalculaArea() override{
        return pow(_raio,2)*M_PI;
    }
};

class Triangulo : public FiguraGeometrica{//subclasse triangulo

    private:
    int _base;
    int _altura;

    public:
    Triangulo(int x, int y, int base, int altura) : FiguraGeometrica(x,y), _base(base), _altura(altura){}

    void Desenha() override{
        FiguraGeometrica::Desenha();
        std::cout << "TRIANGULO" << std::endl;
    }

    float CalculaArea() override{
        return _base*_altura/2.0;
    }
};

int main(){
    std::vector<FiguraGeometrica*> Figuras;
    int x,y,dimensao1,dimensao2;
    float area;
    char comando;

    do{
        std::cin>>comando;

        switch (comando)
        {
            case 'R':{//gera um retangulo dinamicamente e adiciona ao vetor de figuras
                std::cin >> x >> y >> dimensao1 >> dimensao2;
                Figuras.push_back(new Retangulo(x,y,dimensao1,dimensao2));
                break;
            }

            case 'C':{//gera um ciruclo dinamicamente e adiciona ao vetor de figuras
                std::cin >> x >> y >> dimensao1;
                Figuras.push_back(new Circulo(x,y,dimensao1));
                break;
            }

            case 'T':{//gera um triangulo dinamicamente e adiciona ao vetor de figuras
                std::cin >> x >> y >> dimensao1 >> dimensao2;
                Figuras.push_back(new Triangulo(x,y,dimensao1,dimensao2));
                break;
            }

            case 'D':{//desenha todas as figuras do vetor
                for(auto busca : Figuras){
                    (*busca).Desenha();
                }
                break;
            }

            case 'A':{//retorna a área total das figuras
                area=0;
                for(auto busca : Figuras){
                    area += (*busca).CalculaArea();
                }
                std::cout << std::fixed << std::setprecision(2) << area << std::endl;
                break;
            }
        
            default:
            break;  
        }

    }while(comando != 'E');

    for(auto busca : Figuras){//deleta todas as figuras do vetor
        delete busca;
    }
}