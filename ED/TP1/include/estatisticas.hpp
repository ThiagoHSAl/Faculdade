#ifndef ESTATISTICAS_HPP
#define ESTATISTICAS_HPP

//usa unsigned long long int para permitir boa análise experimental
typedef struct estatisticas{
  unsigned long long int cmp;
  unsigned long long int move;
  unsigned long long int calls;
} estatisticas;

#endif