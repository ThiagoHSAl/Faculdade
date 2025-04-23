#include "TipoCelula.hpp"

TipoCelula::TipoCelula()
{
    item = -1;
    proximo = nullptr;
}

TipoCelula::TipoCelula(int item)
{
    this->item = item;
    proximo = nullptr;
}