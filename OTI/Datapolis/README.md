# Datapólis

Plataforma web de transparência pública que reúne indicadores sociais e de gestão dos
**5.570 municípios brasileiros** em um só lugar. O usuário navega por um mapa interativo do
Brasil (colorido por uma nota geral de 0 a 5), busca uma cidade pelo nome e consulta a página
de indicadores, podendo ainda comparar dois municípios lado a lado.

Projeto Aplicado da disciplina **OTI071 — Organização e Tratamento da Informação**
(Sistemas de Informação, UFMG), no challenge *Dados Abertos, IA e Impacto Social*.

## Funcionalidades

- **Mapa interativo do Brasil** (D3.js): estados coloridos pela nota média; ao clicar em um
  estado, faz zoom e carrega a malha municipal, com tooltip por município e botão de retorno.
- **Busca com autocomplete**: sugestões de municípios em tempo real via API, disponível na
  home e na barra de navegação das páginas internas.
- **Página do município**: indicadores de orçamento, educação, saúde, segurança e assistência
  social, com variação (delta) em relação ao período anterior.
- **Comparação por semelhança**: lista automaticamente os 5 municípios com população mais
  próxima e mostra a média deles como referência, além da média nacional do IDEB.
- **Comparação direta**: seleção de uma segunda cidade e confronto dos indicadores lado a lado.
- **Nota geral 0–5**: índice sintético calculado a partir dos indicadores, usado para colorir
  o mapa e resumir a situação do município.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Python 3 + Flask 3.0 |
| Templates | Jinja2 (HTML) |
| Banco de dados | SQLite (`datapolis.db`) |
| Frontend | HTML/CSS + JavaScript puro, D3.js v7 para o mapa |
| Deploy | Gunicorn (`Procfile`) |

## Estrutura do repositório

```
Datapolis/
├── app.py                  # Backend Flask: rotas, APIs e cálculo da nota geral
├── datapolis.db            # Base SQLite com os 5.570 municípios
├── requirements.txt        # Dependências Python
├── Procfile                # web: gunicorn app:app
├── static/
│   ├── style.css
│   ├── mapa.js             # Mapa D3: estados, zoom, malha municipal e cores por nota
│   ├── search.js           # Autocomplete reutilizável (home e navbar)
│   └── Logo1.jpeg, logo2.jpeg
└── templates/
    ├── index.html                  # Home: hero, busca e mapa
    ├── municipio.html              # Página de indicadores do município
    ├── selecionar_comparacao.html  # Escolha da segunda cidade
    ├── comparacao.html             # Comparação lado a lado
    └── components/                 # navbar.html, footer.html
```

## Como executar

```bash
# 1. Ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate

# 2. Dependências
pip install -r requirements.txt

# 3. Servidor de desenvolvimento
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco `datapolis.db` já vem populado no
repositório, então não é preciso rodar nenhuma carga inicial.

Para produção:

```bash
gunicorn app:app
```

## Rotas

### Páginas

| Rota | Descrição |
| --- | --- |
| `GET /` | Home com busca e mapa do Brasil |
| `GET /municipio/<codigo_ibge>` | Página de indicadores do município |
| `GET /indicadores` | Redireciona para o último município visitado (padrão: Belo Horizonte, 3106200) |
| `GET /comparar/<cod1>` | Seleção da segunda cidade para comparação |
| `GET /comparar/<cod1>/<cod2>` | Comparação lado a lado |

### APIs

| Rota | Retorno |
| --- | --- |
| `GET /api/search?q=<texto>` | JSON com até 10 municípios cujo nome contém o texto |
| `GET /api/notas-mapa` | JSON com `{municipios: {codigo: nota}, estados: {uf: nota}}` — consumido pelo mapa |

## Modelo de dados

Tabela única `municipios`, com o **código IBGE de 7 dígitos como chave primária** — identificador
oficial que permite integrar as diferentes fontes de dados abertos e casar os registros com a
malha geográfica do mapa.

| Bloco | Campos | Fonte |
| --- | --- | --- |
| Identificação e demografia | `codigo_ibge`, `nome`, `uf`, `regiao`, `capital`, `populacao` | IBGE |
| Orçamento (% do total) | `despesa_educacao_pct`, `despesa_saude_pct`, `despesa_administracao_pct`, `despesa_seguranca_pct`, `despesa_infraestrutura_pct`, `despesa_outros_pct` | SICONFI / Tesouro Nacional |
| Educação | `ideb_anos_iniciais` (0–10), `ideb_delta` | INEP |
| Saúde | `cobertura_aps` (%), `mortalidade_infantil` (por mil nascidos vivos), `mortalidade_delta` | DATASUS |
| Segurança | `ocorrencias_criminais` (por 100 mil hab.), `ocorrencias_delta` | SINESP |
| Assistência social | `bolsa_familia_beneficiarios`, `bolsa_familia_delta` | MDS |
| Economia e síntese | `pib_per_capita`, `nota_geral` | IBGE / calculado |

## Cálculo da nota geral (0–5)

Média ponderada dos indicadores disponíveis, normalizados para a escala 0–5. Indicadores
ausentes são ignorados e os pesos são renormalizados pelo total efetivamente usado, de modo
que municípios com dados incompletos ainda recebem uma nota comparável.

| Indicador | Peso | Normalização |
| --- | --- | --- |
| PIB per capita | 20% | proporcional, teto em R$ 60.000 |
| IDEB anos iniciais | 20% | direta (escala 0–10) |
| Cobertura da Atenção Primária | 15% | direta (escala 0–100%) |
| Mortalidade infantil | 15% | **inversa**, referência de 60 óbitos/mil |
| Ocorrências criminais | 15% | **inversa**, referência de 5.000 por 100 mil |
| Gasto com saúde (%) | 15% | proporcional, teto em 30% do orçamento |

Implementação em `calcular_nota_municipio()` (`app.py:33`).

## Fontes externas do mapa

As malhas geográficas são carregadas em tempo de execução via CDN:

- Estados: [`codeforamerica/click_that_hood`](https://github.com/codeforamerica/click_that_hood)
- Municípios por UF: [`tbrugz/geodata-br`](https://github.com/tbrugz/geodata-br)

Ou seja, o mapa depende de acesso à internet mesmo rodando localmente.

## Limitações conhecidas

- Os dados são um **retrato estático**: não há pipeline automatizado de atualização; a base é
  regenerada manualmente a partir das fontes abertas.
- Alguns municípios têm indicadores faltantes nas fontes originais (`NULL` no banco); nesses
  casos a nota geral é calculada apenas com o que existe, ou omitida se não houver nenhum dado.
- Os tetos de normalização da nota (R$ 60.000 de PIB per capita, 30% de gasto com saúde, etc.)
  são escolhas de projeto e não padrões oficiais — servem para tornar municípios comparáveis,
  não para classificá-los oficialmente.
- A `secret_key` do Flask está fixa no código, adequada apenas ao uso acadêmico atual; em um
  ambiente real deve vir de variável de ambiente.

## Contexto acadêmico

Disciplina OTI071 — Organização e Tratamento da Informação
Departamento de Organização e Tratamento da Informação — UFMG
Curso: Sistemas de Informação
