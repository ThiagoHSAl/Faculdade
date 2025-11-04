#include "cidade.hpp"
#include <iostream>
#include <queue>
#include <limits>
#include <cmath>
#include <stdexcept>

#define ValorLimiteLLint std::numeric_limits<LL>::max()
#define INFINITO std::numeric_limits<LL>::max()

// Getters simples
LL Rua::getDestino() const { 
    return destino; 
}
LL Rua::getComprimento() const { 
    return comprimento; 
}
LL Rua::getIndice() const { 
    return indice; 
}


//verifica se uma a rua UV está em pelo menos um caminho minimo de Origem a Destino
bool Rua::estaEmUmCaminhoMinimo(LL distDaOrigemAU, LL distDeVAoDestino, LL menorDistanciaTotal) const {

    // Verificação de overflow de long long int com os parâmetros recebidos
    if (distDaOrigemAU > ValorLimiteLLint - this->comprimento || (distDaOrigemAU + this->comprimento) > ValorLimiteLLint - distDeVAoDestino) {
        throw std::overflow_error("Erro: Overflow ao calcular distâncias.");
    }
    
    if (distDaOrigemAU + this->comprimento + distDeVAoDestino == menorDistanciaTotal){
        return true;
    }
    else {
        return false;
    }
}


//verifica se uma rua UV é critica, baseado em caminhos mínimos
bool Rua::eCritica(LL caminhosMinimosDaOrigemAU, LL caminhosMinimosdeVAoDestino, LL numeroTotalDeCaminhosMinimos) const {

    // Verificação para evitar divisão por zero e lógica incorreta
    if (numeroTotalDeCaminhosMinimos == 0 || caminhosMinimosdeVAoDestino == 0 || caminhosMinimosDaOrigemAU == 0) {
        return false;
    }

    if (numeroTotalDeCaminhosMinimos % caminhosMinimosdeVAoDestino != 0) {
        return false; // Se a divisão não for exata, o produto não pode ser igual
    }

    // Verificação segura contra overflow na multiplicação
    if (caminhosMinimosDaOrigemAU == numeroTotalDeCaminhosMinimos / caminhosMinimosdeVAoDestino){
        return true;
    } 
    
    else {
        return false;
    }
}

//Construtor que inicializa o grafo com o número de bairros especificado
Cidade::Cidade(LL numBairros) {
    if (numBairros < 0) {
        throw std::invalid_argument("Erro: Número de bairros deve ser positivo");
    }
    grafoCidade.resize(numBairros);
}  


//Adiciona uma Rua bidirecional entre os bairros 'origem' e 'destino' com a 'distancia' especificada
void Cidade::adicionarRua(LL indice, LL origem, LL destino, LL distancia) {
    LL numBairros = static_cast<LL>(grafoCidade.size());

    if (origem < 0 || origem >= numBairros || destino < 0 || destino >= numBairros) {
        throw std::out_of_range("Erro: Bairro de origem ou destino inválido.");
    }

    if (distancia <= 0) {
        throw std::invalid_argument("Erro: Distância deve ser um número positivo.");
    }

    Rua novaRua = {indice, distancia, destino};
    grafoCidade[origem].push_back(novaRua);
    Rua RuaReversa = {indice, distancia, origem};
    grafoCidade[destino].push_back(RuaReversa);
}


// Versão 1: Retorna um vetor com as distâncias mínimas a partir do bairro 'origem' para todos os outros bairros
void Cidade::dijkstra(LL origem, std::vector<LL>& distancias) const {
    dijkstra_core(origem, distancias, nullptr);
}


// Versão 2: Retorna o mesmo vetor de distancias minimas
//Atualiza um vetor com o número de caminhos mínimos a partir do bairro 'origem' para todos os outros bairros
void Cidade::dijkstra(LL origem, std::vector<LL>& distancias, std::vector<LL>& numCaminhosMinimos) const {
    dijkstra_core(origem, distancias, &numCaminhosMinimos);
}


// Se o ponteiro for nulo, a lógica de contagem de caminhos minimos é pulada.
void Cidade::dijkstra_core(LL origem, std::vector<LL>& distancias, std::vector<LL>* numCaminhosMinimos) const {
    const LL numVertices = static_cast<LL>(grafoCidade.size());

    if (origem < 0 || origem >= numVertices) {
        throw std::out_of_range("Erro: Bairro de origem inválido.");
    }
    
    distancias.assign(numVertices, INFINITO);

    if (numCaminhosMinimos != nullptr) {
        numCaminhosMinimos->assign(numVertices, 0);
        (*numCaminhosMinimos)[origem] = 1;
    }

    distancias[origem] = 0;
    
    // Min-heap baseado na distância
    std::priority_queue<Rua, std::vector<Rua>, std::greater<Rua>> pq;
    pq.push({0, origem});

    while (!pq.empty()) {
        LL distAtual = pq.top().getComprimento();
        LL u = pq.top().getDestino();
        pq.pop();

        // otimizacao, este caminho é mais longo que o melhor conhecido
        if (distAtual > distancias[u]) continue;

        // Explora todas as ruas adjacentes ao bairro u
        for (const auto& ruaUV : grafoCidade[u]) {
            LL v = ruaUV.getDestino();
            LL comprimento = ruaUV.getComprimento();

            if (distancias[u] > ValorLimiteLLint - comprimento){
                throw std::overflow_error("Erro: Overflow ao calcular distâncias.");
            }

            LL novaDistancia = distancias[u] + comprimento;

            //encontrou um caminho mais curto para v
            if (novaDistancia < distancias[v]) {
                distancias[v] = novaDistancia;
                pq.push({distancias[v], v});

                if (numCaminhosMinimos != nullptr) {
                    //o numero de caminhos minimos para v é igual ao número de caminhos minimos para u
                    (*numCaminhosMinimos)[v] = (*numCaminhosMinimos)[u];
                }
            }

            //encontrou um caminho alternativo para v com o mesmo comprimento minimo
            else if (novaDistancia == distancias[v]) {
                if (numCaminhosMinimos != nullptr) {
                    //como é um caminho alternativo, agora tenho novos caminhos minimos que devem ser somados
                    (*numCaminhosMinimos)[v] += (*numCaminhosMinimos)[u];
                }
            }
        }
    }
}


// Retorna a menor distância entre os bairros 'origem' e 'destino'
LL Cidade::buscarMenorCaminho(LL origem, LL destino) {
    LL numBairros = static_cast<LL>(grafoCidade.size());
    
    if (origem < 0 || origem >= numBairros || destino < 0 || destino >= numBairros) {
        throw std::out_of_range("Erro: Bairro de origem ou destino inválido.");
    }

    std::vector<LL> distanciasDesdeAOrigem;
    //dijkstra versão 1, apenas distâncias
    dijkstra(origem, distanciasDesdeAOrigem);

    if (distanciasDesdeAOrigem.empty()) {
        throw std::runtime_error("Erro na execução do Dijkstra.");
    }
    
    if (distanciasDesdeAOrigem[destino] == INFINITO) {
        return -1; // Não há caminho entre origem e destino
    }

    return distanciasDesdeAOrigem[destino];
}


// Retorna os índices das ruas que fazem parte de pelo menos um caminho mínimo entre 'origem' e 'destino'
std::set<LL> Cidade::encontrarRuasEmUmCaminhoMinimo(LL origem, LL destino) {
    LL numBairros = static_cast<LL>(grafoCidade.size());

    if (origem < 0 || origem >= numBairros || destino < 0 || destino >= numBairros) {
        throw std::out_of_range("Erro: Bairro de origem ou destino inválido.");
    }
    
    std::vector<LL> distanciasDesdeAOrigem;
    //nao preciso contar quantos caminhos minimos, um caminho minimo ja é suficiente
    dijkstra(origem, distanciasDesdeAOrigem);
    
    LL menorDistanciaTotal = distanciasDesdeAOrigem[destino];

    // Se não há caminho entre origem e destino, não há ruas em um caminho mínimo
    if (menorDistanciaTotal == INFINITO) {
        return {};
    }

    //dijkstra a partir do destino para obter distâncias reversas
    std::vector<LL> distanciasDesdeODestino;
    dijkstra(destino, distanciasDesdeODestino);
    
    std::set<LL> indicesRuasEmUmCaminhoMinimo;

    // Iteramos sobre todas as ruas para verificar se estão em algum caminho mínimo
    for (LL u = 0; u < numBairros; ++u) {
        for (const auto& ruaUV : grafoCidade[u]) {
            LL v = ruaUV.getDestino();
            LL daOrigemAteU = distanciasDesdeAOrigem[u];
            LL doDestinoAteV = distanciasDesdeODestino[v];
            LL indiceRua = ruaUV.getIndice();

            if (ruaUV.estaEmUmCaminhoMinimo(daOrigemAteU, doDestinoAteV, menorDistanciaTotal)) {
                indicesRuasEmUmCaminhoMinimo.insert(indiceRua);
            }
        }
    }

    return indicesRuasEmUmCaminhoMinimo;
}


// Retorna os índices das ruas críticas entre 'origem' e 'destino'
std::set<LL> Cidade::encontrarRuasCriticas(LL origem, LL destino) {
    LL numBairros = static_cast<LL>(grafoCidade.size());

    if (origem < 0 || origem >= numBairros || destino < 0 || destino >= numBairros) {
        throw std::out_of_range("Erro: Bairro de origem ou destino inválido.");
    }

    std::vector<LL> distanciasDesdeAOrigem, numeroDeCaminhosMinimosDesdeAOrigem;
    //Versão 2: agora vamos contar os caminhos mínimos
    dijkstra(origem, distanciasDesdeAOrigem, numeroDeCaminhosMinimosDesdeAOrigem);
    
    LL menorDistanciaTotal = distanciasDesdeAOrigem[destino];

    if (menorDistanciaTotal == INFINITO) {
        return {};
    }

    std::vector<LL> distanciasDesdeODestino, numeroDeCaminhosMinimosDesdeODestino;
    dijkstra(destino, distanciasDesdeODestino, numeroDeCaminhosMinimosDesdeODestino);
    LL totalDeCaminhosMinimos = numeroDeCaminhosMinimosDesdeAOrigem[destino];

    std::set<LL> indicesRuasCriticas;
   
    //Iteramos sobre todas as ruas verificando se são críticas
    for (LL u = 0; u < numBairros; ++u) {
        for (const auto& ruaUV : grafoCidade[u]) {
            LL v = ruaUV.getDestino();
            LL daOrigemAU = distanciasDesdeAOrigem[u];
            LL deVAteODestino = distanciasDesdeODestino[v];

            if (ruaUV.estaEmUmCaminhoMinimo(daOrigemAU, deVAteODestino, menorDistanciaTotal)) {
                LL caminhosMinimosDaOrigemAU = numeroDeCaminhosMinimosDesdeAOrigem[u];
                LL caminhosMinimosDoDestinoAV = numeroDeCaminhosMinimosDesdeODestino[v];
                LL indiceRua = ruaUV.getIndice();
                
                if (ruaUV.eCritica(caminhosMinimosDaOrigemAU, caminhosMinimosDoDestinoAV, totalDeCaminhosMinimos)) {
                    indicesRuasCriticas.insert(indiceRua);
                }
            }
        }
    }

    return indicesRuasCriticas;
}

