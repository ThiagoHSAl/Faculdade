# LoL AI Tutor Benchmarks API

API para consulta de benchmarks, estatísticas agregadas e panorama do meta de partidas ranqueadas de League of Legends.

## Base URL

```text
http://129.213.153.233:8000
```

---

# Visão Geral

A API disponibiliza três conjuntos principais de dados:

1. **Benchmarks pré-calculados**

   * Benchmark médio de um elo.
   * Benchmark de uma divisão específica.
   * Benchmark dos elos Apex.

2. **Pesquisa avançada**

   * Permite consultar estatísticas agregadas utilizando filtros personalizados.

3. **Panorama do Meta**

   * Top campeões por elo e posição.
   * Taxa de vitória.
   * Tamanho da amostra.
   * Top itens utilizados.

Todas as respostas são retornadas em formato JSON.

A API pode ser consumida utilizando qualquer cliente HTTP compatível, incluindo:

* cURL
* Python (`requests`)
* JavaScript (`fetch`)
* Postman
* Insomnia
* Aplicações backend em qualquer linguagem

---

# Endpoints

## Benchmarks

```http
GET /benchmarks/todos

GET /benchmarks/{elo}
GET /benchmarks/{elo}/{divisao}

GET /benchmarks/campeoes/{posicao}?campeoes=Jinx,Caitlyn

GET /benchmarks/rota/{posicao}
GET /benchmarks/rota/{posicao}/{elo}
GET /benchmarks/rota/{posicao}/{elo}/{divisao}
```

Parâmetros de consulta comuns às rotas de benchmark por rota:

* `regiao` — agrega apenas aquela região direto do banco (`br1`, `na1`, `euw1`, `kr`). Sem ele, usa o cache global.
* `fila` — fila ranqueada/normal (`solo`, `flex`, `normal`).

---

## Pesquisa Avançada

```http
GET /pesquisa-avancada
```

---

## Panorama do Meta

```http
GET /panorama-meta/{elo}
```

---

# 1. Todos os Benchmarks

Retorna todos os benchmarks armazenados em cache.

## Endpoint

```http
GET /benchmarks/todos
```

## Exemplo

```bash
curl -s "http://129.213.153.233:8000/benchmarks/todos"
```

---

# 2. Benchmark por Elo ou Divisão

Permite consultar benchmarks de forma flexível.

## Endpoint

```http
GET /benchmarks/{elo}
```

ou

```http
GET /benchmarks/{elo}/{divisao}
```

---

## Consulta por Elo

Quando apenas o elo é informado, a API retorna a média das quatro divisões daquele elo.

### Exemplo

```bash
curl -s "http://129.213.153.233:8000/benchmarks/GOLD"
```

A consulta acima retorna a média calculada utilizando:

```text
GOLD_I
GOLD_II
GOLD_III
GOLD_IV
```

O mesmo comportamento ocorre para:

```text
IRON
BRONZE
SILVER
GOLD
PLATINUM
EMERALD
DIAMOND
```

---

## Consulta por Elo e Divisão

Quando elo e divisão são informados, a API retorna apenas os dados daquela divisão.

### Exemplo

```bash
curl -s "http://129.213.153.233:8000/benchmarks/GOLD/II"
```

Retorna exclusivamente os benchmarks de Gold II.

---

## Elos Apex

Para os elos Apex, não é necessário informar divisão.

### Exemplos

```bash
curl -s "http://129.213.153.233:8000/benchmarks/MASTER"

curl -s "http://129.213.153.233:8000/benchmarks/GRANDMASTER"

curl -s "http://129.213.153.233:8000/benchmarks/CHALLENGER"
```

Internamente a API utiliza:

```text
MASTER_I
GRANDMASTER_I
CHALLENGER_I
```

Também é possível utilizar:

```text
/benchmarks/MASTER/I
/benchmarks/GRANDMASTER/I
/benchmarks/CHALLENGER/I
```

Porém a divisão será ignorada.

---

## Elos Suportados

```text
IRON
BRONZE
SILVER
GOLD
PLATINUM
EMERALD
DIAMOND
MASTER
GRANDMASTER
CHALLENGER
```

---

## Divisões Suportadas

```text
I
II
III
IV
```

---

# 3. Benchmark por Rota

Os benchmarks acima são gerais do elo/divisão. As rotas abaixo restringem o benchmark a uma
**posição** específica (e opcionalmente a uma região ou fila), servindo o cálculo de elo
equivalente e a avaliação por rota.

## Rota em todos os elos

```http
GET /benchmarks/rota/{posicao}
```

Retorna o benchmark da rota em todos os elos, ordenados hierarquicamente (Iron → Challenger).

```bash
curl -s "http://129.213.153.233:8000/benchmarks/rota/MIDDLE"
curl -s "http://129.213.153.233:8000/benchmarks/rota/MIDDLE?regiao=kr&fila=solo"
```

## Rota em um elo/divisão

```http
GET /benchmarks/rota/{posicao}/{elo}
GET /benchmarks/rota/{posicao}/{elo}/{divisao}
```

Apenas o elo faz a média das divisões `I..IV`; os elos Apex ignoram a divisão.

```bash
curl -s "http://129.213.153.233:8000/benchmarks/rota/JUNGLE/DIAMOND"
curl -s "http://129.213.153.233:8000/benchmarks/rota/JUNGLE/DIAMOND/II"
curl -s "http://129.213.153.233:8000/benchmarks/rota/BOTTOM/CHALLENGER"
```

## Rota restrita a um conjunto de campeões

```http
GET /benchmarks/campeoes/{posicao}?campeoes=Jinx,Caitlyn,Ashe
```

Benchmark de uma rota calculado só sobre um campeão (mono) ou um *pool* de campeões. Sem `?elo=`,
retorna todos os elos ordenados; com `?elo=`, faz a média das divisões daquele elo. Se a amostra
for insuficiente para os campeões informados, retorna `404`.

```bash
curl -G "http://129.213.153.233:8000/benchmarks/campeoes/BOTTOM" \
     --data-urlencode "campeoes=Jinx,Caitlyn,Ashe" \
     --data-urlencode "elo=DIAMOND"
```

---

# 4. Pesquisa Avançada

Permite consultar estatísticas agregadas utilizando filtros opcionais.

## Endpoint

```http
GET /pesquisa-avancada
```

Todos os parâmetros são opcionais e podem ser combinados livremente.

Quanto mais filtros forem utilizados, mais específica será a amostra analisada.

---

## Parâmetros Suportados

### campeao

Filtra os dados para um campeão específico.

Exemplos:

```text
Yasuo
Ahri
Lee Sin
Thresh
```

---

### posicao

Filtra o desempenho do campeão em uma função específica no mapa.

Valores suportados:

```text
TOP
JUNGLE
MIDDLE
BOTTOM
UTILITY
```

---

### elo

Filtra as estatísticas pelo elo dos jogadores.

Valores suportados:

```text
IRON
BRONZE
SILVER
GOLD
PLATINUM
EMERALD
DIAMOND
MASTER
GRANDMASTER
CHALLENGER
```

---

### divisao

Filtra a subdivisão dentro do elo.

Valores suportados:

```text
I
II
III
IV
```

---

### regiao

Filtra os dados conforme o servidor/região de coleta.

Valores suportados:

```text
br1
na1
euw1
kr
```

---

### vitoria

Filtra as estatísticas com base no resultado final da partida.

Valores suportados:

```text
1 -> Apenas vitórias

0 -> Apenas derrotas
```

---

# Exemplos de Pesquisa Avançada

## Estatísticas gerais de um campeão

```bash
curl -G "http://129.213.153.233:8000/pesquisa-avancada" \
     --data-urlencode "campeao=Yasuo"
```

---

## Campeão em uma posição específica

```bash
curl -G "http://129.213.153.233:8000/pesquisa-avancada" \
     --data-urlencode "campeao=Yasuo" \
     --data-urlencode "posicao=MIDDLE"
```

---

## Campeão em um elo específico

```bash
curl -G "http://129.213.153.233:8000/pesquisa-avancada" \
     --data-urlencode "campeao=Yasuo" \
     --data-urlencode "elo=CHALLENGER"
```

---

## Apenas vitórias

```bash
curl -G "http://129.213.153.233:8000/pesquisa-avancada" \
     --data-urlencode "campeao=Yasuo" \
     --data-urlencode "elo=CHALLENGER" \
     --data-urlencode "vitoria=1"
```

---

## Consulta completa

Partidas de Yasuo:

* Rota do meio
* Challenger
* Região KR
* Apenas vitórias

```bash
curl -G "http://129.213.153.233:8000/pesquisa-avancada" \
     --data-urlencode "campeao=Yasuo" \
     --data-urlencode "posicao=MIDDLE" \
     --data-urlencode "elo=CHALLENGER" \
     --data-urlencode "regiao=kr" \
     --data-urlencode "vitoria=1"
```

### Exemplo em Python

```python
import requests

url = "http://129.213.153.233:8000/pesquisa-avancada"

params = {
    "campeao": "Yasuo",
    "posicao": "MIDDLE",
    "elo": "CHALLENGER",
    "regiao": "kr",
    "vitoria": 1
}

response = requests.get(url, params=params)

print(response.json())
```

---

# Estrutura da Resposta da Pesquisa Avançada

```json
{
  "amostra_partidas": 1523,
  "taxa_vitoria_porcento": 53.12,

  "metricas_basicas": {
    "kda": 4.21,
    "cs_min": 8.43,
    "ouro_min": 472.18,
    "visao_min": 1.52
  },

  "combate_e_impacto": {
    "dano_min": 812.51,
    "dano_objetivos": 4231.34,
    "dano_torres": 2789.13,
    "dano_mitigado": 15421.51,
    "cura_total": 512.84,
    "pct_dano_time_porcento": 27.33
  },

  "early_game_e_agressividade": {
    "first_blood_rate_porcento": 14.92,
    "first_blood_assist_rate_porcento": 11.24,
    "solo_kills": 1.41,
    "cs_rota_10m": 78.15,
    "cs_jungle_10m": 0
  },

  "utilidade_e_mapa": {
    "pink_wards_compradas": 2.14,
    "tempo_cc_causado": 8.31,
    "tempo_vivo_segundos": 1483.22,
    "skillshots_desviadas": 14.83
  },

  "comunicacao_pings": {
    "pings_perigo": 5.21,
    "pings_ajuda": 2.03,
    "pings_mia": 1.87
  }
}
```

---

# 5. Panorama do Meta

Retorna uma visão consolidada do meta para um elo específico.

Os dados são pré-processados e servidos a partir de cache para máxima performance.

## Endpoint

```http
GET /panorama-meta/{elo}
```

---

## Exemplo

```bash
curl -s "http://129.213.153.233:8000/panorama-meta/CHALLENGER"
```

---

## Estrutura da Resposta

Para cada posição do jogo são retornados:

* Top 10 campeões por taxa de vitória.
* Win Rate.
* Tamanho da amostra.
* Top 5 itens mais utilizados.

Exemplo:

```json
{
  "MIDDLE": [
    {
      "campeao": "Ahri",
      "winrate": 53.24,
      "amostra": 1843,
      "top_5_itens": [
        "Companheiro de Luden",
        "Chama Sombria",
        "Capuz da Morte de Rabadon",
        "Ampulheta de Zhonya",
        "Cajado do Vazio"
      ]
    }
  ]
}
```

---

## Posições Disponíveis

```text
TOP
JUNGLE
MIDDLE
BOTTOM
UTILITY
```

---

# Sistema de Itens

A API obtém automaticamente os nomes dos itens através do Riot Data Dragon.

Isso garante compatibilidade automática com novos patches e atualizações do jogo.

---

# Imagens dos Itens

Os itens podem ser exibidos utilizando diretamente as imagens oficiais da Riot Games.

Formato:

```text
https://ddragon.leagueoflegends.com/cdn/{versao}/img/item/{item_id}.png
```

Exemplo:

```text
https://ddragon.leagueoflegends.com/cdn/15.12.1/img/item/3157.png
```

---

# Versão Mais Recente do Jogo

A API detecta automaticamente a versão mais recente disponível no Riot Data Dragon.

Essa funcionalidade é utilizada para:

* Atualização automática dos itens.
* Compatibilidade com novos patches.
* Atualização das imagens.
* Sincronização com o meta atual.

Caso a consulta falhe, um valor de fallback é utilizado para manter a disponibilidade do serviço.

---

# Sistema de Cache

Para garantir baixa latência, a API serve a maioria das respostas a partir de quatro arquivos
de cache em JSON, todos regenerados periodicamente por um processo em segundo plano
(o serviço `atualizador`):

## cache_benchmarks.json

Benchmarks gerais agregados por elo e divisão.

## cache_benchmarks_rota.json

Benchmarks segmentados por rota (posição) × elo × divisão — base das rotas `/benchmarks/rota/*`.

## cache_percentis_rota.json

Grades de percentis por rota e elo, usadas para posicionar cada métrica do jogador dentro do
seu próprio elo/rota.

## cache_panorama.json

Panorama do meta: top campeões, taxa de vitória, tamanho da amostra e top itens por posição.

Consultas com `?regiao=` são agregadas direto do banco (fora do cache global). Enquanto um cache
inicial ainda não existe, a rota correspondente responde `503`.

---

# Tratamento de Erros

## Nenhum dado encontrado

```json
{
  "mensagem": "Nenhum dado encontrado para essa combinação de filtros."
}
```

---

## Benchmark inexistente

```json
{
  "detail": "Benchmark não encontrado."
}
```

HTTP Status:

```text
404 Not Found
```

---

## Cache ainda não disponível

```json
{
  "detail": "Aguarde. O cache inicial está sendo gerado pelo servidor."
}
```

HTTP Status:

```text
503 Service Unavailable
```

---

## Elo inválido para panorama

```json
{
  "detail": "Elo inválido."
}
```

HTTP Status:

```text
400 Bad Request
```

---

# Observações

* Todos os filtros textuais são case-insensitive.
* É possível utilizar qualquer combinação de filtros.
* Quanto mais filtros forem aplicados, mais específica será a amostra retornada.
* Quando apenas o elo é informado, a API retorna a média das divisões daquele elo.
* Para MASTER, GRANDMASTER e CHALLENGER não é necessário informar divisão.
* Todos os resultados representam médias agregadas calculadas sobre as partidas que satisfazem os filtros informados.
* O panorama do meta é atualizado automaticamente através do sistema de cache.
* Os nomes dos itens são obtidos dinamicamente do Riot Data Dragon.
* As imagens dos itens permanecem sincronizadas com a versão mais recente do jogo.
* A API foi projetada para servir dados diretamente para aplicações de IA, dashboards e sistemas de coaching automatizado.

