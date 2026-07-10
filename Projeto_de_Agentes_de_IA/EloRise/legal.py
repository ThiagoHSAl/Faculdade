"""
legal.py — Textos legais do EloRise: disclaimer da Riot (boilerplate obrigatório da
política de terceiros), Termos de Uso e Política de Privacidade (LGPD).

Mantidos num módulo próprio para o app.py não inchar e para a revisão/atualização dos
textos ser um diff isolado. Ao alterar um texto, atualize VERSAO_LEGAL — a data aparece
no rodapé dos documentos.
"""

VERSAO_LEGAL = "08/07/2026"
EMAIL_CONTATO = "thiagohenriquesilva.a@gmail.com"

# Boilerplate exigido pela política de desenvolvedores da Riot (Legal Jibber Jabber).
# O texto oficial é em inglês; a linha em português resume para o usuário brasileiro.
DISCLAIMER_RIOT = (
    "O EloRise não é endossado pela Riot Games e não reflete as visões ou opiniões da "
    "Riot Games ou de qualquer pessoa oficialmente envolvida na produção ou gestão das "
    "propriedades da Riot Games. Riot Games e League of Legends são marcas registradas "
    "da Riot Games, Inc.\n\n"
    "*EloRise isn't endorsed by Riot Games and doesn't reflect the views or opinions of "
    "Riot Games or anyone officially involved in producing or managing Riot Games "
    "properties. Riot Games, and all associated properties are trademarks or registered "
    "trademarks of Riot Games, Inc.*"
)

TERMOS_USO = f"""
### Termos de Uso — EloRise

*Última atualização: {VERSAO_LEGAL}*

**1. O serviço.** O EloRise é uma ferramenta de análise e tutoria para jogadores de
League of Legends: compara as suas métricas de jogo com médias agregadas do seu elo e
rota, conversa com você por meio de um tutor de inteligência artificial e monta planos
de treino pessoais. Os dados de partidas vêm da API oficial da Riot Games.

**2. Conta.** Você pode entrar com a sua conta Google ou criar uma conta local
(usuário e senha). Você é responsável por manter a confidencialidade das suas
credenciais. Uma conta por pessoa; contas usadas para abuso (automação, scraping,
sobrecarga do serviço) podem ser encerradas.

**3. Uso aceitável.** O EloRise serve para você avaliar e melhorar o **seu próprio**
jogo. Não use o serviço para assediar, expor ou depreciar outros jogadores.

**4. O tutor é uma IA.** As análises e conselhos são gerados por modelos de linguagem
a partir dos seus dados de jogo e de uma base de conhecimento tática. Podem conter
imprecisões; use o próprio julgamento. O EloRise não garante resultado competitivo
(subir de elo) nem disponibilidade ininterrupta do serviço.

**5. Gratuidade.** O serviço é atualmente gratuito. Caso planos pagos venham a existir,
haverá sempre um nível gratuito de acesso, e estes termos serão atualizados com
antecedência.

**6. Propriedade intelectual.** League of Legends e todos os dados, imagens e nomes
associados pertencem à Riot Games, Inc. (ver aviso abaixo). O código, a marca e os
textos do EloRise pertencem ao seu desenvolvedor.

**7. Encerramento e exclusão.** Você pode excluir a sua conta e todos os dados
associados a qualquer momento pelo próprio app (menu "Minha conta"). Podemos encerrar
o serviço ou contas que violem estes termos.

**8. Alterações.** Estes termos podem mudar; a data no topo indica a versão vigente.
Mudanças relevantes serão sinalizadas no app.

**9. Contato.** Dúvidas e solicitações: **{EMAIL_CONTATO}**.

---

{DISCLAIMER_RIOT}
"""

POLITICA_PRIVACIDADE = f"""
### Política de Privacidade — EloRise

*Última atualização: {VERSAO_LEGAL} · Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018)*

**1. Controlador.** O EloRise é operado por seu desenvolvedor, contatável em
**{EMAIL_CONTATO}** — canal também usado para solicitações de titulares de dados.

**2. Dados que coletamos.**
- **Conta**: e-mail e nome (login Google) ou nome de usuário (conta local; a senha é
  armazenada apenas como hash criptográfico — nunca em texto claro).
- **Uso do serviço**: nicks de jogador pesquisados, rota analisada, conversas com o
  tutor, planos de treino e progresso.
- **Cookies**: um único cookie de sessão (`elorise_sessao`, validade de 30 dias) para
  manter o login local ativo. Sem cookies de rastreamento ou publicidade.

**3. Para que usamos.** Exclusivamente para prestar o serviço: gerar suas análises,
manter o histórico das suas conversas e planos entre sessões e manter você conectado.
Não vendemos nem compartilhamos seus dados para fins de marketing.

**4. Com quem os dados transitam (operadores).**
- **Riot Games** — consultamos a API oficial com o nick pesquisado para obter dados
  públicos de partidas.
- **Google** — o login Google (OAuth) e o modelo de IA (Gemini) que gera as respostas
  do tutor; o conteúdo das conversas é processado pelo Gemini para gerar as respostas.
- **Supabase** — banco de dados onde contas, conversas e planos ficam armazenados.
- **Streamlit Community Cloud (Snowflake)** — hospedagem do aplicativo.

**5. Retenção.** Seus dados ficam armazenados enquanto a conta existir. Ao excluir a
conta, todos os dados associados (perfil, análises, conversas, planos e sessões de
login) são apagados imediatamente e de forma definitiva.

**6. Seus direitos (LGPD, art. 18).** Acesso, correção, portabilidade e eliminação dos
seus dados. A eliminação está disponível diretamente no app ("Minha conta" → "Excluir
minha conta"); para os demais, escreva para **{EMAIL_CONTATO}**.

**7. Segurança.** Senhas com hash scrypt (padrão OWASP), tokens de sessão armazenados
apenas como hash, credenciais de serviço fora do código-fonte e acesso ao banco
restrito ao aplicativo.

**8. Menores de idade.** O serviço segue a classificação etária do próprio League of
Legends e não coleta intencionalmente dados além dos listados acima.

**9. Alterações.** A data no topo indica a versão vigente desta política.
"""
