# EloRise — Documentação do Sistema

EloRise é um agente de tutoria para *League of Legends* que diagnostica o desempenho do
jogador e conduz uma tutoria socrática fundamentada em dados reais. Combina a Riot API, um
backend próprio de *benchmarks* segmentados por rota, elo e divisão, e um agente LLM (Gemini
via LangGraph) com ferramentas próprias, mantendo memória por jogador entre sessões.

## Arquitetura

- **Frontend:** Streamlit (`app.py`) — interface conversacional e visualizações (Plotly/Altair).
- **Agente:** LangGraph + Gemini (`tutor_interativo.py`) — grafo de estados com memória por
  `thread_id`, *tool-calling* e auto-crítica determinística do formato socrático.
- **Backend de benchmarks:** API HTTP externa (FastAPI, hospedada à parte) que serve estatísticas
  agregadas por rota/elo/divisão; endereço via variável `BENCHMARKS_API_URL`.
- **Dados:** Riot API (`Match-V5`, `League-V4`) e Data Dragon (itens, campeões, runas, feitiços).

## Módulos (raiz do repositório)

| Arquivo | Papel |
|---|---|
| `app.py` | Frontend Streamlit (ponto de entrada). |
| `tutor_interativo.py` | Agente LangGraph: ferramentas, *prompt* de sistema e auto-crítica socrática. |
| `generate_stats.py` | Coleta da Riot API e montagem do diagnóstico (elo equivalente, pior métrica). |
| `config.py` | Configuração via ambiente, métricas por rota (`ROLE_METRICS`), rótulos e ordem de elos. |
| `riot_client.py` | *Wrapper* da Riot API com tratamento de *rate limit* e *backoff*. |
| `deteccao_rota.py` | Inferência da rota efetivamente jogada (não apenas o `teamPosition`). |
| `base_conhecimento.py` | Base de conhecimento tática (curada + Data Dragon) e busca por palavra-chave. |
| `rag.py` | Recuperação semântica e híbrida (embeddings do Gemini + similaridade de cosseno). |
| `datadragon.py` | Geração da base factual (`conhecimento_datadragon.json`) a partir do Data Dragon. |
| `analise_partidas.py` | Análise da *timeline* (mortes, padrões recorrentes, objetivos). |
| `viz_partidas.py` | Visualizações das partidas. |
| `plano_treino.py` | Plano de treino estruturado e verificável. |
| `insights_evolucao.py` | Insights de evolução após a definição do plano. |
| `explicar_drill.py` | Explicação dos *drills* de treino. |
| `persistencia.py` | Persistência das sessões do tutor. |
| `auth.py` | Login: Google (OIDC nativo do Streamlit) + conta local com hash *scrypt* de *fallback*. |
| `legal.py` | Textos legais: disclaimer da Riot, Termos de Uso e Política de Privacidade (LGPD). |

## Fluxo de execução

1. O jogador informa *nick* e servidor; `generate_stats` coleta as últimas partidas via Riot API.
2. A rota é inferida (`deteccao_rota`), as métricas são agregadas por rota e o diagnóstico é montado
   contra o *benchmark* do elo (elo equivalente e pior métrica).
3. O agente (`tutor_interativo`) decide autonomamente quais ferramentas chamar e conduz a tutoria
   socrática, com memória por jogador e plano de treino.
4. A recuperação (`base_conhecimento` + `rag`) fundamenta os conceitos táticos citados.

## Como executar

1. `pip install -r requirements.txt`
2. Criar um arquivo `.env` na raiz com, no mínimo:
   - `RIOT_PERSONAL_KEY` — chave da Riot API do app (aceita `RIOT_API_KEY` como *fallback*);
   - `GEMINI_API_KEY` — chave do Google Gemini;
   - `BENCHMARKS_API_URL` — URL do backend de benchmarks (padrão: `http://129.213.153.233:8000`);
   - opcionais: `LOL_PLATFORM` (ex.: `br1`), `LOL_REGION` (ex.: `americas`).
   - login com Google (opcional): seção `[auth]` em `.streamlit/secrets.toml` (ver `secrets.toml.example`).
3. `streamlit run app.py`

## Índice de conhecimento (RAG)

O índice de embeddings (`kb_embeddings.npz`) é gerado offline por `python rag.py` (construção
incremental e resiliente à cota do Gemini) e não é versionado.

## Segurança

As credenciais residem exclusivamente no `.env` (nunca no código nem no histórico de versão).
Ver também a documentação da API de benchmarks em `API_DOCUMENTACAO.md`.
