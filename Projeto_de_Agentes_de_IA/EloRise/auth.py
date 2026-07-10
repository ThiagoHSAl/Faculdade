"""
auth.py — Login do EloRise: Google (OIDC nativo do Streamlit) + conta local (fallback).

Padrão de mercado aplicado aqui:
  * Caminho preferido: DELEGAR a autenticação via OIDC (st.login/st.user) — nenhuma
    senha é armazenada e o MFA vem de graça do Google. Ativado quando existe a seção
    [auth] no .streamlit/secrets.toml (ver secrets.toml.example) e o Authlib instalado.
  * Fallback local: usuário+senha próprios com hash scrypt (recomendação OWASP; ver
    persistencia.py), mensagens de erro genéricas (não revelam se o usuário existe)
    e trava progressiva contra força bruta (5 erros → espera de 30s).

O login local SOBREVIVE ao F5 com um cookie "lembrar de mim": no login emitimos um
token de sessão (30 dias; o banco guarda só o hash — persistencia.criar_sessao_auth)
e o gravamos via JS num components.html (o iframe srcdoc herda a origem do app, então
document.cookie vale para o domínio); num reload, o st.context.cookies (que vem do
handshake do WebSocket) resolve o token de volta para o usuário. O logout revoga o
token no banco — o cookie que sobrar no navegador vira letra morta. Limite honesto:
cookie gravado por JS não tem HttpOnly (um XSS conseguiria lê-lo); o caminho Google
usa o cookie de sessão do próprio Streamlit e dispensa isso tudo.

A gravação/limpeza do cookie é DIFERIDA (flags no session_state consumidas por
exigir_login) porque um st.rerun imediatamente após renderizar o components.html
descartaria o iframe antes de o JS executar.
"""
import os
import time

import streamlit as st

from persistencia import (autenticar_local, criar_usuario_local, obter_ou_criar_usuario_oidc,
                          criar_sessao_auth, usuario_por_token, revogar_sessao_auth)

_MAX_TENTATIVAS = 5
_ESPERA_S = 30
_COOKIE = "elorise_sessao"
_DIAS_SESSAO = 30


def _executar_js(script: str) -> None:
    """Roda JS no navegador via components.html — iframe srcdoc que herda a origem do
    app e EXECUTA scripts, então document.cookie vale para o domínio. (st.iframe não
    serve: o parâmetro é uma URL, o HTML virava um src inválido e o JS nunca rodava —
    era por isso que o login local não sobrevivia ao F5.) ELORISE_SEM_COOKIE_JS
    desliga a emissão — o AppTest (testes) não suporta o elemento de componente."""
    if os.environ.get("ELORISE_SEM_COOKIE_JS"):
        return
    import streamlit.components.v1 as components
    try:
        components.html(f"<script>{script}</script>", height=1)
    except Exception:
        pass


def _gravar_cookie(token: str) -> None:
    """Grava o cookie de sessão no navegador (SameSite=Lax; Secure sob HTTPS)."""
    _executar_js(
        "const seguro = (window.parent.location.protocol === 'https:') ? '; Secure' : '';"
        f"document.cookie = \"{_COOKIE}={token}; path=/; max-age={_DIAS_SESSAO * 86400}\""
        " + '; SameSite=Lax' + seguro;"
    )


def _apagar_cookie() -> None:
    _executar_js(f"document.cookie = \"{_COOKIE}=; path=/; max-age=0\";")


def _ler_cookie_navegador() -> str | None:
    """Lê o cookie de sessão DIRETO do navegador (document.cookie via streamlit_js_eval).
    Necessário no Streamlit Community Cloud: o proxy da plataforma só repassa o
    _streamlit_xsrf ao servidor (comprovado em produção), então st.context.cookies
    nunca contém cookies próprios lá. O componente devolve None no primeiro run e o
    valor num rerun seguinte — quem chama precisa tolerar o atraso de um ciclo."""
    if os.environ.get("ELORISE_SEM_COOKIE_JS"):
        return None
    try:
        from streamlit_js_eval import streamlit_js_eval
        bruto = streamlit_js_eval(js_expressions="document.cookie", key="ler_cookie_sessao")
    except Exception:
        return None
    for parte in str(bruto or "").split(";"):
        nome, _, valor = parte.strip().partition("=")
        if nome == _COOKIE and valor:
            return valor
    return None


def _oidc_disponivel() -> bool:
    """Google OIDC ligado = Streamlit com st.login + Authlib + [auth] no secrets.toml."""
    if not hasattr(st, "login"):
        return False
    try:
        import authlib  # noqa: F401
    except ImportError:
        return False
    try:
        return "auth" in st.secrets
    except Exception:  # sem secrets.toml
        return False


def usuario_atual() -> dict | None:
    """Usuário logado ({id, identificador, nome, metodo}) ou None. Ordem: sessão já
    resolvida → OIDC do Streamlit → cookie "lembrar de mim" (F5 do login local).
    A sessão vem primeiro para não ir ao banco A CADA rerun (o logout limpa a chave;
    trocar de conta Google derruba a sessão do Streamlit, então o cache não vaza)."""
    user = st.session_state.get("auth_user")
    if user:
        return user
    if _oidc_disponivel() and getattr(st.user, "is_logged_in", False):
        user = obter_ou_criar_usuario_oidc(st.user.email, getattr(st.user, "name", None))
        st.session_state.auth_user = user
        return user
    try:
        token = st.context.cookies.get(_COOKIE)
    except Exception:  # contexto sem cookies (ex.: testes bare)
        token = None
    if not token:
        # Streamlit Cloud: o proxy não repassa cookies próprios ao servidor —
        # lê do navegador (chega num rerun; até lá seguimos sem usuário).
        token = _ler_cookie_navegador()
    user = usuario_por_token(token)
    if user:
        st.session_state.auth_user = user
        st.session_state.auth_token = token  # p/ revogação no logout (Cloud não repassa o cookie)
    return user


def sair() -> None:
    """Logout: revoga o token do cookie no banco (o cookie restante fica inválido),
    agenda a limpeza do cookie no navegador e derruba a sessão."""
    try:
        revogar_sessao_auth(st.session_state.get("auth_token")
                            or st.context.cookies.get(_COOKIE))
    except Exception:
        pass
    st.session_state.pop("auth_token", None)
    st.session_state.pop("auth_user", None)
    st.session_state.auth_cookie_limpar = True
    if _oidc_disponivel() and getattr(st.user, "is_logged_in", False):
        st.logout()  # limpa o cookie OIDC e recarrega
    else:
        st.rerun()


def _trava_forca_bruta() -> bool:
    """True se a sessão está em cooldown por excesso de tentativas."""
    falhas = st.session_state.get("auth_falhas", 0)
    if falhas < _MAX_TENTATIVAS:
        return False
    restante = _ESPERA_S - (time.time() - st.session_state.get("auth_ultima_falha", 0))
    if restante > 0:
        st.error(f"Muitas tentativas. Aguarde {int(restante) + 1}s e tente novamente.")
        return True
    st.session_state.auth_falhas = 0
    return False


def _registrar_falha() -> None:
    st.session_state.auth_falhas = st.session_state.get("auth_falhas", 0) + 1
    st.session_state.auth_ultima_falha = time.time()


def _entrar_local(user: dict) -> None:
    """Sessão local aberta: emite o token de 30 dias e agenda a gravação do cookie
    (feita pelo exigir_login no próximo run, já na tela logada)."""
    st.session_state.auth_user = user
    st.session_state.auth_falhas = 0
    st.session_state.auth_token_pendente = criar_sessao_auth(user["id"], _DIAS_SESSAO)
    st.rerun()


def _form_login_local() -> None:
    with st.form("login_local"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", width="stretch"):
            if _trava_forca_bruta():
                return
            user = autenticar_local(usuario, senha)
            if user:
                _entrar_local(user)
            else:
                _registrar_falha()
                st.error("Usuário ou senha inválidos.")


def _form_cadastro_local() -> None:
    with st.form("cadastro_local"):
        usuario = st.text_input("Usuário (3+ caracteres: letras, números, _)")
        nome = st.text_input("Nome de exibição (opcional)")
        senha = st.text_input("Senha (8+ caracteres)", type="password")
        senha2 = st.text_input("Confirme a senha", type="password")
        if st.form_submit_button("Criar conta", width="stretch"):
            if senha != senha2:
                st.error("As senhas não conferem.")
                return
            try:
                _entrar_local(criar_usuario_local(usuario, senha, nome or None))
            except ValueError as e:
                st.error(str(e))


def exigir_login(render_cabecalho=None, render_rodape=None) -> dict:
    """Gate de autenticação: devolve o usuário logado ou desenha a tela de login e
    INTERROMPE o script (st.stop). Chamar no topo do app, antes de qualquer dado.
    `render_rodape` desenha o rodapé legal (termos/privacidade) também na tela de
    login — o usuário precisa poder ler as políticas ANTES de criar a conta."""
    user = usuario_atual()
    if user:
        # Cookie pendente do login local: gravado aqui, na tela logada estável (sem
        # rerun em seguida), para o JS do iframe ter tempo de executar.
        token = st.session_state.pop("auth_token_pendente", None)
        if token:
            st.session_state.auth_token = token
            _gravar_cookie(token)
        return user

    if st.session_state.pop("auth_cookie_limpar", False):
        _apagar_cookie()

    if render_cabecalho:
        render_cabecalho()
    st.write("")

    _, centro, _ = st.columns([1, 1.4, 1])
    with centro:
        st.markdown("### Entrar")
        st.caption("Seus dados de mentoria (conversas, planos de treino e progresso) "
                   "ficam salvos no seu perfil.")
        if _oidc_disponivel():
            if st.button("Entrar com Google", width="stretch", type="primary"):
                st.login()
            st.markdown("<div style='text-align:center; opacity:.6'>— ou —</div>",
                        unsafe_allow_html=True)
        else:
            st.caption("Login com Google desativado (configure .streamlit/secrets.toml — "
                       "ver secrets.toml.example).")
        aba_login, aba_cadastro = st.tabs(["Entrar com conta local", "Criar conta"])
        with aba_login:
            _form_login_local()
        with aba_cadastro:
            _form_cadastro_local()
            st.caption("Ao criar a conta você concorda com os Termos de Uso e a "
                       "Política de Privacidade (no rodapé).")
    if render_rodape:
        render_rodape()
    st.stop()
