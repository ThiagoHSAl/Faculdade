# Submissão da Production Key da Riot — pacote pronto

Textos para o formulário do [Riot Developer Portal](https://developer.riotgames.com)
(Register Product → aplicação de produção, League of Legends / Standard APIs).
Redigidos em inglês porque a revisão é do time global de Developer Relations.

> **NOTA INTERNA (10/jul/2026) — estado real ≠ narrativa desta submissão.** O texto abaixo
> afirma que os crawlers estão *PAUSED* e que a Personal Key serve só usuários ao vivo. Hoje o
> estado real é diferente: **os dois crawlers RODAM continuamente**, cada um numa **dev key**
> separada (`RIOT_DEV_KEY`/`RIOT_DEV_KEY2`, que expiram a cada 24h), enquanto a
> `RIOT_PERSONAL_KEY` serve exclusivamente o app (`elorise.com.br`). Ou seja, a intenção
> ("personal key isolada para tráfego ao vivo") continua valendo, mas o *meio* mudou — não estão
> pausados. **Antes de submeter/atualizar a aplicação na Riot, reconciliar isto:** ou pausar os
> crawlers de fato para bater com o texto, ou reescrever a narrativa descrevendo a arquitetura
> real (crawlers em dev keys separadas + personal key dedicada ao app). Esta nota é só interna e
> não faz parte de nada enviado à Riot.

## Product Name

```
EloRise
```

## Product URL

```
https://elorise.com.br
```

## Product Description

O campo pede explicitamente "Be descriptive about how you will be using the
API" com limite de ~1500 caracteres — então o USO DA API vem em primeiro plano
(endpoints, crawlers, rate limiting) e o produto em resumo. Versão abaixo:
1419 chars com o placeholder; ~1441 com link real do YouTube (cabe).

```
EloRise is an AI coaching web app for League of Legends for the Brazilian community (pt-BR UI; ToS, Privacy Policy and Riot disclaimer in PT and EN on the login page).

API usage (live app): when a player requests an analysis we call Account-V1 (by-riot-id), Summoner-V4 (by-puuid), League-V4 (entries/by-puuid) and Match-V5 (ids, match, timeline) — about 6 on-demand calls per analysis. The player's metrics (CS/min, gold/min, vision, damage, objectives and 20+ more) are shown as percentiles within their own rank and role, and an AI tutor turns that diagnosis into training drills and a Socratic tutoring cycle.

API usage (benchmarks): the percentiles come from our own aggregation dataset — 430,000+ ranked matches, all 31 rank strata (Iron IV to Challenger), BR1/NA1/EUW1/KR — built by two crawlers using League-V4 (tier entries + apex leagues) and Match-V5. These crawlers are currently PAUSED so our Personal Key serves only live users; under a production key they will run through a central cross-process rate limiter that derives its pacing from the X-App-Rate-Limit headers and reserves ~30% headroom for live traffic. We store aggregated statistics only, never raw match payloads for redistribution.

Monetization will follow the General Policies: permanent free tier; paid features limited to transformative AI coaching. Users can permanently delete their account and data in one click. Demo video: <LINK>
```

## Notas técnicas (SEM campo no formulário — confirmado em 07/07/2026)

O formulário real só tem **nome, description e URL**. O conteúdo abaixo serve
para a **thread de mensagens da aplicação no portal**: se o portal permitir
enviar mensagem logo após submeter, poste este texto proativamente (mostra
maturidade e antecipa as perguntas clássicas dos revisores — rate limit, dados,
monetização). Senão, guarde como banco de respostas: quando o revisor
perguntar, cole o trecho relevante.

```
CURRENT STATE AND KEY USAGE PLAN

The live app (https://elorise.com.br) currently runs on our Personal
API Key. Per user analysis it makes ~6 on-demand calls: Account-V1
(by-riot-id), Summoner-V4 (by-puuid), League-V4 (entries/by-puuid), Match-V5
(ids, match, timeline). Volume is low and bursty; 429s are honored with
Retry-After backoff.

Our rank benchmarks come from our own aggregation pipeline: two crawlers
(League-V4 entries + apex leagues, Match-V5) that built a 430k-match dataset
across BR1/NA1/EUW1/KR, stored as aggregated per-champion/role/rank statistics.
These crawlers are currently PAUSED: we shut them down so the Personal Key
serves only live users, and they will only resume under the production key.

RATE LIMIT COMPLIANCE

All crawler traffic goes through a central cross-process rate limiter that
derives its pacing dynamically from the X-App-Rate-Limit response headers (so
it adapts to whatever limits the key actually has), reserves ~30% of the app
budget as headroom for live user requests, and applies 429 Retry-After
penalties globally across all processes.

DATA HANDLING

We store aggregated statistics (averages and percentiles per champion, role
and rank), not raw match payloads for redistribution. User-facing data is
per-account, and users can permanently delete their account and all associated
data in one click ("My account" page). Required Riot disclaimer, ToS and
Privacy Policy are displayed on every page of the app.

MONETIZATION INTENT

EloRise is currently 100% free. Once approved, we intend to monetize in
compliance with the General Policies: a permanent free tier (match analysis
and benchmarks), with paid features limited to transformative added value
(deeper AI tutoring sessions, long-term progress coaching). No gambling, no
betting, no sale of Riot data.

INFRASTRUCTURE

Web app self-hosted at https://elorise.com.br (our own domain and VPS, behind
Caddy with automatic HTTPS), alongside the benchmarks API (FastAPI) with a
/health endpoint monitored by UptimeRobot. Contact:
thiagohenriquesilva.a@gmail.com.

REVIEW ACCESS

The product UI is in Brazilian Portuguese, targeting the Brazilian League
community (BR1); the Terms of Service, Privacy Policy and Riot disclaimer are
provided in both Portuguese and English, and are visible on the login page
itself, before any sign-in. To review the full product flow you can
create a local account directly in the app (email + password, no approval
needed), or watch this short demo video: [LINK DO VIDEO AQUI]
```

## Como submeter (passo a passo)

1. Entre em https://developer.riotgames.com com a conta Riot dona do produto
   "EloRise" (a mesma da personal key).
2. No dashboard, abra o produto EloRise existente ou clique em **Register
   Product** e escolha o caminho de **aplicação de produção** (produto de
   larga escala, League of Legends, Standard APIs).
3. Preencha os 3 campos (nome, description, URL) com os textos acima. O campo
   description tem limite de ~1500 caracteres — a versão compacta cabe.
4. **Verificação**: a Riot pode pedir um arquivo `riot.txt` na raiz do domínio
   do produto para provar que ele é seu. Ver "Risco conhecido" abaixo.
5. Submeta. A revisão leva ~2 semanas (10 dias úteis; pode chegar a 3 semanas).
   Aprovação/rejeição e perguntas chegam nas **mensagens da aplicação dentro do
   próprio portal** — checar o portal semanalmente, é lá que se responde.

## ATUALIZAÇÃO 07/07/2026: a verificação por riot.txt CHEGOU

O portal exige riot.txt na raiz da Product URL com o código (RENOVADO na resubmissão de 08/07 — trocar a URL exigiu submeter de novo)
`f1b7563d-1b8f-4980-9eee-4fa7c832e672` — impossível no Streamlit Cloud (não
serve arquivos na raiz nem suporta domínio próprio).

DECISÃO (08/07/2026): `elorise.com.br` será O SITE DA APLICAÇÃO, não um
redirect — o app Streamlit migra do Streamlit Cloud para a VPS (Oracle,
129.80.151.220), atrás do Caddy com HTTPS automático. O Caddy serve
`/riot.txt` na raiz e faz proxy do resto para o Streamlit local (8501).
A VPS comporta: 2 vCPU, ~640MB livres + 2GB swap, 34GB de disco.

Passos (VPS preparada pelo agente; itens marcados [USUÁRIO] são manuais):

1. [USUÁRIO] Registrar `elorise.com.br` no https://registro.br (~R$40/ano).
2. [USUÁRIO] Oracle Cloud Console → VCN → Security List da instância →
   liberar ingress TCP 80 e 443 (0.0.0.0/0), como foi feito para a 8000.
3. VPS — FEITO 08/07/2026: EloRise clonado em ~/EloRise (venv Python 3.11.15),
   secrets.toml com redirect_uri https://elorise.com.br/oauth2callback e
   BENCHMARKS_API_URL=http://127.0.0.1:8000 (localhost, não IP público),
   systemd `elorise.service` (enable+active, health ok, ~73MB idle), Caddy
   v2.11.4 com /riot.txt na raiz + proxy 8501 + www→raiz, iptables 80/443
   persistido (netfilter-persistent). O certificado só emite quando o DNS
   apontar (Caddy re-tenta sozinho).
4. [USUÁRIO] registro.br DNS (modo avançado): registro **A** da raiz →
   `129.80.151.220` e **A** (ou CNAME) `www` → mesmo destino.
5. [USUÁRIO] Google Auth Platform → Credentials → adicionar redirect URI
   `https://elorise.com.br/oauth2callback`.
6. Quando o DNS propagar, o Caddy emite o certificado sozinho. Conferir:
   `curl https://elorise.com.br/riot.txt` → código exato; app abrindo na raiz.
7. No portal da Riot: editar a aplicação, trocar a **Product URL** para
   `https://elorise.com.br` e clicar **Verify URL**.
8. Depois da migração: desligar (ou esvaziar) o app no Streamlit Cloud para
   não haver duas instâncias públicas; secrets de lá podem ser revogados.

O repo local `elorise-site/` (landing + CNAME p/ GitHub Pages) ficou OBSOLETO
com essa decisão — o site é o próprio app.

## Risco conhecido (ANTIGO, confirmado acima): verificação por riot.txt / domínio próprio

O Streamlit Cloud não serve arquivos na raiz (`https://elorise.streamlit.app/riot.txt`
não é possível), e a política diz "in most cases" o produto deve estar num
domínio próprio. Se a Riot exigir a verificação:

- **Opção A (barata e rápida)**: registrar um domínio (ex.: `elorise.com.br`,
  ~R$40/ano) e usar Cloudflare (grátis) na frente — serve o `riot.txt` via
  regra/Worker e redireciona o resto para o streamlit.app. O domínio vira a
  Product URL.
- **Opção B (roadmap etapa 6)**: mover o front para a VPS atrás do domínio
  próprio. Mais trabalho; só faz sentido com tração.

Se o formulário não exigir riot.txt para web apps, submeter com a URL do
Streamlit mesmo e resolver domínio só se os revisores pedirem.

Nota do FAQ oficial (Production Key Applications): a exigência de domínio
próprio é enfatizada para apps NATIVOS/mobile/bots de Discord — para web apps o
site em si é o produto, e o que a Riot quer VER é o fluxo de uso + ToS +
Privacidade. O EloRise cumpre isso na própria URL do Streamlit. O FAQ também
aceita video demos e screenshots como material de demonstração — dai o campo
de video em REVIEW ACCESS.

## Antes de submeter (checklist)

- [ ] Gravar demo de 2-3 min (login → análise de partida → percentis → drills →
      ciclo socrático → panorama → "Minha conta"/exclusão), subir como não
      listado no YouTube e substituir o <LINK> no fim da description.
- [ ] Confirmar que criar conta local funciona sem aprovação manual (revisor
      precisa entrar sozinho).
- [ ] UptimeRobot verde há alguns dias.
- [ ] Após submeter: se a aplicação tiver thread de mensagens no portal,
      postar lá o texto de "Notas técnicas" proativamente.

## Fatos que sustentam a submissão (já no ar em 07/07/2026)

- Legal/LGPD: disclaimer da Riot, Termos, Privacidade (pt+en) em todas as
  telas; exclusão total de conta (commit `9a5c292` do EloRise).
- Crawlers pausados aguardando a production key; rate limiter central lendo
  `X-App-Rate-Limit` (commits `e6e30f2`/`13fc7ab` do lol-api).
- `/health` + UptimeRobot na API de benchmarks.
- Dataset próprio: 433k partidas / 4,3M linhas, 31 estratos de elo, 4 regiões.
