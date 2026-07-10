"""
persistencia.py — Memória de longo prazo do tutor, MULTIUSUÁRIO, com DOIS backends.

Cada dado pertence a um usuário logado (ver auth.py): o thiago que pesquisa
"seravini#BR1" tem a própria conversa/plano; outro login que pesquise o mesmo nick
começa do zero. A interface mantém UMA conversa salva por (usuário, jogador, rota) —
a troca de contexto é pelo seletor de rota da tela do perfil — mas o esquema suporta
várias por slot (listar/nova/selecionar/excluir_conversa ficam para uso futuro);
o plano de treino e o histórico de planos são um por rota.

Backends (decidido em tempo de execução, por conexão):
  * SQLite local (elorise.db) — desenvolvimento/uso local; zero configuração.
  * Postgres (Supabase) quando DATABASE_URL está no ambiente ou no st.secrets —
    obrigatório no Streamlit Community Cloud, cujo disco é EFÊMERO (um SQLite lá
    zeraria contas e conversas a cada redeploy).
A classe _Conexao uniformiza os dialetos (placeholders '?', INSERT OR IGNORE,
linhas acessáveis por nome, commit/close ao sair do with). Ids novos são obtidos
com RETURNING id (funciona nos dois; requer SQLite >= 3.35).

Esquema:
    usuarios     — contas (locais com hash scrypt de senha, ou Google OIDC sem senha)
    sessoes_auth — tokens de sessão do login local (cookie "lembrar de mim"; ver auth.py)
    jogadores    — por (user_id, jogador): rota_atual, servidor e metricas_superadas
    rotas        — por (user_id, jogador, rota): plano, historico_planos e conversa ativa
    conversas    — cada conversa salva: título, mensagens (JSON) e tutoria_encerrada
    meta         — flags internas (ex.: migração do sessoes_tutor.json legado)

O sessoes_tutor.json antigo (single-user) é migrado UMA vez, para o primeiro usuário
que fizer login — os dados legados eram do dono da instalação.
"""
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

_DB = Path(__file__).resolve().parent / "elorise.db"
_JSON_LEGADO = Path(__file__).resolve().parent / "sessoes_tutor.json"

# Parâmetros do scrypt (recomendação OWASP para uso interativo): N=2^14, r=8, p=1.
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1


def _chave(game_name: str, tag_line: str) -> str:
    """Chave canônica do jogador: normaliza CADA parte (espaços das pontas, runs de
    espaço internos e caixa) — "dogla la dogla " e "dogla la dogla" são o MESMO jogador."""
    gn = " ".join((game_name or "").split())
    tl = " ".join((tag_line or "").split()).lstrip("#")
    return f"{gn}#{tl}".lower()


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _url_postgres() -> str | None:
    """DATABASE_URL do ambiente ou do st.secrets (Streamlit Cloud). Ausente = SQLite."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    try:
        import streamlit as st
        return st.secrets.get("DATABASE_URL")
    except Exception:
        return None


_POOL = None
_POOL_LOCK = threading.Lock()


def _pool_pg(url: str):
    """Pool de conexões do Postgres (singleton do processo): abrir TCP+TLS+auth a cada
    operação custava ~3 RTTs até o pooler do Supabase (centenas de ms do Streamlit
    Cloud); reusar a conexão corta para ~1 RTT por operação. `check=` testa a conexão
    ao emprestar e descarta as que o servidor derrubou no ocioso; max_size baixo
    respeita o limite do Session pooler do plano free."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is None:
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
            _POOL = ConnectionPool(
                url, min_size=0, max_size=4, open=True,
                check=ConnectionPool.check_connection,
                kwargs={"row_factory": dict_row},
            )
        return _POOL


class _Conexao:
    """Uniformiza sqlite3 e psycopg atrás de uma API única: execute() com
    placeholders '?', linhas acessáveis por nome, e commit (ou rollback) ao sair
    do with. No Postgres a conexão vem do pool (devolvida na saída); no SQLite
    continua uma conexão por operação — simples e seguro entre as threads das
    sessões do Streamlit."""

    def __init__(self):
        url = _url_postgres()
        self.pg = bool(url)
        if self.pg:
            self._pool = _pool_pg(url)
            self.con = self._pool.getconn()
        else:
            self.con = sqlite3.connect(_DB, timeout=15)
            self.con.row_factory = sqlite3.Row
            self.con.execute("PRAGMA journal_mode=WAL")
            self.con.execute("PRAGMA foreign_keys=ON")

    def execute(self, sql: str, params=()):
        if self.pg:
            if sql.lstrip().startswith("INSERT OR IGNORE"):
                sql = sql.replace("INSERT OR IGNORE", "INSERT", 1) + " ON CONFLICT DO NOTHING"
            sql = sql.replace("?", "%s")
        return self.con.execute(sql, params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.con.commit()
            else:
                self.con.rollback()
        finally:
            if self.pg:
                self._pool.putconn(self.con)
            else:
                self.con.close()


def _conectar() -> _Conexao:
    return _Conexao()


def _ddl(pg: bool) -> list[str]:
    # Única diferença de dialeto: a coluna de id autoincrementado.
    id_auto = ("INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY" if pg
               else "INTEGER PRIMARY KEY AUTOINCREMENT")
    return [
        f"""CREATE TABLE IF NOT EXISTS usuarios (
                id            {id_auto},
                identificador TEXT UNIQUE NOT NULL,
                nome          TEXT,
                senha_hash    TEXT,
                criado_em     TEXT
            )""",
        """CREATE TABLE IF NOT EXISTS sessoes_auth (
                token_hash TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                criado_em  TEXT,
                expira_em  TEXT
            )""",
        """CREATE TABLE IF NOT EXISTS jogadores (
                user_id             INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                jogador             TEXT NOT NULL,
                rota_atual          TEXT,
                servidor            TEXT,
                metricas_superadas  TEXT DEFAULT '{}',
                atualizado_em       TEXT,
                PRIMARY KEY (user_id, jogador)
            )""",
        """CREATE TABLE IF NOT EXISTS rotas (
                user_id           INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                jogador           TEXT NOT NULL,
                rota              TEXT NOT NULL,
                plano             TEXT,
                historico_planos  TEXT DEFAULT '[]',
                conversa_ativa    INTEGER,
                PRIMARY KEY (user_id, jogador, rota)
            )""",
        f"""CREATE TABLE IF NOT EXISTS conversas (
                id                {id_auto},
                user_id           INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                jogador           TEXT NOT NULL,
                rota              TEXT NOT NULL,
                titulo            TEXT,
                mensagens         TEXT DEFAULT '[]',
                tutoria_encerrada INTEGER DEFAULT 0,
                criado_em         TEXT,
                atualizado_em     TEXT
            )""",
        "CREATE INDEX IF NOT EXISTS idx_conversas_slot ON conversas (user_id, jogador, rota)",
        """CREATE TABLE IF NOT EXISTS meta (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )""",
    ]


def _init_db() -> None:
    with _conectar() as con:
        for stmt in _ddl(con.pg):
            con.execute(stmt)


_init_db()


# ---------------------------------------------------------------------------
# Usuários (camada de dados usada por auth.py)
# ---------------------------------------------------------------------------

def _hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    h = hashlib.scrypt(senha.encode("utf-8"), salt=sal,
                       n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${sal.hex()}${h.hex()}"


def _verificar_senha(senha: str, guardado: str) -> bool:
    try:
        _, n, r, p, sal_hex, hash_hex = guardado.split("$")
        h = hashlib.scrypt(senha.encode("utf-8"), salt=bytes.fromhex(sal_hex),
                           n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(h.hex(), hash_hex)  # comparação em tempo constante
    except Exception:
        return False


def criar_usuario_local(username: str, senha: str, nome: str = None) -> dict:
    """Cadastra uma conta local. Levanta ValueError se o username já existir ou for inválido."""
    username = (username or "").strip().lower()
    if not username or len(username) < 3 or not username.replace("_", "").isalnum():
        raise ValueError("Nome de usuário inválido: use 3+ caracteres (letras, números, _).")
    if len(senha or "") < 8:
        raise ValueError("A senha precisa ter pelo menos 8 caracteres.")
    ident = f"local:{username}"
    with _conectar() as con:
        if con.execute("SELECT 1 FROM usuarios WHERE identificador=?", (ident,)).fetchone():
            raise ValueError("Esse nome de usuário já existe.")
        row = con.execute(
            "INSERT INTO usuarios (identificador, nome, senha_hash, criado_em)"
            " VALUES (?,?,?,?) RETURNING id",
            (ident, nome or username, _hash_senha(senha), _agora())).fetchone()
        user = {"id": row["id"], "identificador": ident,
                "nome": nome or username, "metodo": "local"}
    _migrar_json_legado(user["id"])
    return user


def autenticar_local(username: str, senha: str) -> dict | None:
    """Retorna o usuário se username+senha conferem; None caso contrário (mensagem genérica
    fica a cargo da UI, para não revelar se o usuário existe)."""
    ident = f"local:{(username or '').strip().lower()}"
    with _conectar() as con:
        row = con.execute("SELECT * FROM usuarios WHERE identificador = ?", (ident,)).fetchone()
    if not row or not row["senha_hash"] or not _verificar_senha(senha or "", row["senha_hash"]):
        return None
    _migrar_json_legado(row["id"])
    return {"id": row["id"], "identificador": ident, "nome": row["nome"], "metodo": "local"}


def obter_ou_criar_usuario_oidc(email: str, nome: str = None) -> dict:
    """Conta vinculada ao login Google (st.login). Sem senha armazenada."""
    ident = f"google:{(email or '').strip().lower()}"
    with _conectar() as con:
        row = con.execute("SELECT * FROM usuarios WHERE identificador = ?", (ident,)).fetchone()
        if row:
            uid, nome_db = row["id"], row["nome"]
        else:
            novo = con.execute(
                "INSERT INTO usuarios (identificador, nome, criado_em) VALUES (?,?,?)"
                " RETURNING id", (ident, nome or email, _agora())).fetchone()
            uid, nome_db = novo["id"], nome or email
    _migrar_json_legado(uid)
    return {"id": uid, "identificador": ident, "nome": nome_db, "metodo": "google"}


# ---------------------------------------------------------------------------
# Sessões de login persistentes (cookie "lembrar de mim" do login local)
# ---------------------------------------------------------------------------

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_sessao_auth(user_id: int, dias: int = 30) -> str:
    """Emite um token de sessão (aleatório, 256 bits) e guarda SÓ o hash — um vazamento
    do banco não permite forjar cookies. Devolve o token cru para virar cookie."""
    token = secrets.token_urlsafe(32)
    expira = (datetime.now() + timedelta(days=dias)).isoformat(timespec="seconds")
    with _conectar() as con:
        con.execute("INSERT INTO sessoes_auth (token_hash, user_id, criado_em, expira_em)"
                    " VALUES (?,?,?,?)", (_hash_token(token), user_id, _agora(), expira))
    return token


def usuario_por_token(token: str) -> dict | None:
    """Resolve o cookie de sessão de volta para o usuário (None se inválido/expirado).
    Aproveita para varrer tokens vencidos."""
    if not token or not isinstance(token, str):
        return None
    with _conectar() as con:
        con.execute("DELETE FROM sessoes_auth WHERE expira_em < ?", (_agora(),))
        row = con.execute(
            "SELECT u.id, u.identificador, u.nome FROM sessoes_auth s"
            " JOIN usuarios u ON u.id = s.user_id WHERE s.token_hash = ?",
            (_hash_token(token),)).fetchone()
    if not row:
        return None
    metodo = "google" if row["identificador"].startswith("google:") else "local"
    return {"id": row["id"], "identificador": row["identificador"],
            "nome": row["nome"], "metodo": metodo}


def revogar_sessao_auth(token: str) -> None:
    """Invalida o token no logout — o cookie que sobrar no navegador vira letra morta."""
    if not token:
        return
    with _conectar() as con:
        con.execute("DELETE FROM sessoes_auth WHERE token_hash = ?", (_hash_token(token),))


# ---------------------------------------------------------------------------
# Migração do formato antigo (sessoes_tutor.json, single-user)
# ---------------------------------------------------------------------------

def _migrar_json_legado(user_id: int) -> None:
    """Importa o sessoes_tutor.json (uma única vez) para o PRIMEIRO usuário que logar —
    os dados legados pertenciam ao dono da instalação single-user."""
    if not _JSON_LEGADO.exists():
        return
    with _conectar() as con:
        if con.execute("SELECT valor FROM meta WHERE chave='json_migrado'").fetchone():
            return
        try:
            dados = json.loads(_JSON_LEGADO.read_text(encoding="utf-8"))
        except Exception:
            dados = {}
        for jogador, reg in (dados or {}).items():
            if "rotas" not in reg:  # formato pré-histórico (flat): rota única no topo
                rota = reg.get("rota") or (reg.get("plano") or {}).get("posicao")
                reg = {"rota_atual": rota, "metricas_superadas": reg.get("metricas_superadas", {}),
                       "rotas": {rota: reg} if rota else {}}
            con.execute(
                "INSERT OR IGNORE INTO jogadores (user_id, jogador, rota_atual, metricas_superadas,"
                " atualizado_em) VALUES (?,?,?,?,?)",
                (user_id, jogador, reg.get("rota_atual"),
                 json.dumps(reg.get("metricas_superadas") or {}, ensure_ascii=False), _agora()))
            for rota, slot in (reg.get("rotas") or {}).items():
                cid = None
                if slot.get("mensagens"):
                    novo = con.execute(
                        "INSERT INTO conversas (user_id, jogador, rota, titulo, mensagens,"
                        " tutoria_encerrada, criado_em, atualizado_em) VALUES (?,?,?,?,?,?,?,?)"
                        " RETURNING id",
                        (user_id, jogador, rota, _titulo_automatico(slot["mensagens"]),
                         json.dumps(slot["mensagens"], ensure_ascii=False),
                         int(bool(slot.get("tutoria_encerrada"))), _agora(), _agora())).fetchone()
                    cid = novo["id"]
                con.execute("INSERT OR IGNORE INTO rotas (user_id, jogador, rota) VALUES (?,?,?)",
                            (user_id, jogador, rota))
                con.execute(
                    "UPDATE rotas SET plano=?, historico_planos=?, conversa_ativa=?"
                    " WHERE user_id=? AND jogador=? AND rota=?",
                    (json.dumps(slot.get("plano"), ensure_ascii=False) if slot.get("plano") else None,
                     json.dumps(slot.get("historico_planos") or [], ensure_ascii=False), cid,
                     user_id, jogador, rota))
        con.execute("INSERT OR IGNORE INTO meta (chave, valor) VALUES ('json_migrado', ?)",
                    (_agora(),))


# ---------------------------------------------------------------------------
# Sessão do tutor (conversa + plano) — mesma API de antes, com user_id na frente
# ---------------------------------------------------------------------------

# Sentinela: distingue "não mexer neste campo" de um valor real (inclusive None/[]).
_MANTER = object()


def _titulo_automatico(mensagens: list) -> str:
    """Título da conversa = primeira fala do usuário (truncada); senão, a data."""
    for m in mensagens or []:
        if m.get("role") == "user" and m.get("content"):
            txt = " ".join(m["content"].split())
            return txt[:60] + ("…" if len(txt) > 60 else "")
    return f"Conversa de {datetime.now().strftime('%d/%m/%Y %H:%M')}"


def _garantir_jogador(con, user_id: int, jogador: str, rota: str = None,
                      servidor: str = None) -> None:
    con.execute(
        "INSERT OR IGNORE INTO jogadores (user_id, jogador, atualizado_em) VALUES (?,?,?)",
        (user_id, jogador, _agora()))
    sets, vals = ["atualizado_em=?"], [_agora()]
    if rota:
        sets.append("rota_atual=?"); vals.append(rota)
    if servidor:
        sets.append("servidor=?"); vals.append(servidor)
    con.execute(f"UPDATE jogadores SET {', '.join(sets)} WHERE user_id=? AND jogador=?",
                (*vals, user_id, jogador))


def _garantir_rota(con, user_id: int, jogador: str, rota: str):
    con.execute("INSERT OR IGNORE INTO rotas (user_id, jogador, rota) VALUES (?,?,?)",
                (user_id, jogador, rota))
    return con.execute("SELECT * FROM rotas WHERE user_id=? AND jogador=? AND rota=?",
                       (user_id, jogador, rota)).fetchone()


def _garantir_conversa_ativa(con, user_id: int, jogador: str, rota: str) -> int:
    """Devolve o id da conversa ativa do slot, criando uma vazia se não houver."""
    slot = _garantir_rota(con, user_id, jogador, rota)
    if slot["conversa_ativa"]:
        ok = con.execute("SELECT 1 FROM conversas WHERE id=? AND user_id=?",
                         (slot["conversa_ativa"], user_id)).fetchone()
        if ok:
            return slot["conversa_ativa"]
    novo = con.execute(
        "INSERT INTO conversas (user_id, jogador, rota, criado_em, atualizado_em)"
        " VALUES (?,?,?,?,?) RETURNING id",
        (user_id, jogador, rota, _agora(), _agora())).fetchone()
    con.execute("UPDATE rotas SET conversa_ativa=? WHERE user_id=? AND jogador=? AND rota=?",
                (novo["id"], user_id, jogador, rota))
    return novo["id"]


def carregar_sessao(user_id: int, game_name: str, tag_line: str, rota: str = None) -> dict:
    """Retorna {mensagens, tutoria_encerrada, plano, historico_planos, metricas_superadas,
    rota, rota_atual, conversa_id, titulo} da ROTA pedida (ou da última rota ativa), lendo a
    CONVERSA ATIVA do slot (cria uma vazia se preciso, para o thread do agente ser estável)."""
    jogador = _chave(game_name, tag_line)
    with _conectar() as con:
        reg = con.execute("SELECT * FROM jogadores WHERE user_id=? AND jogador=?",
                          (user_id, jogador)).fetchone()
        alvo = rota or (reg["rota_atual"] if reg else None)
        base = {
            "mensagens": [], "tutoria_encerrada": False, "plano": None,
            "historico_planos": [],
            "metricas_superadas": json.loads(reg["metricas_superadas"]) if reg else {},
            "rota": alvo, "rota_atual": reg["rota_atual"] if reg else None,
            "conversa_id": None, "titulo": None,
        }
        if not alvo:
            return base
        _garantir_jogador(con, user_id, jogador, rota=alvo if rota else None)
        cid = _garantir_conversa_ativa(con, user_id, jogador, alvo)
        slot = con.execute("SELECT * FROM rotas WHERE user_id=? AND jogador=? AND rota=?",
                           (user_id, jogador, alvo)).fetchone()
        conv = con.execute("SELECT * FROM conversas WHERE id=?", (cid,)).fetchone()
        base.update({
            "mensagens": json.loads(conv["mensagens"] or "[]"),
            "tutoria_encerrada": bool(conv["tutoria_encerrada"]),
            "plano": json.loads(slot["plano"]) if slot["plano"] else None,
            "historico_planos": json.loads(slot["historico_planos"] or "[]"),
            "conversa_id": cid, "titulo": conv["titulo"],
        })
        return base


def salvar_sessao(user_id: int, game_name: str, tag_line: str, rota: str = None,
                  mensagens=_MANTER, tutoria_encerrada=_MANTER, plano=_MANTER,
                  metricas_superadas=_MANTER, historico_planos=_MANTER,
                  conversa_id: int = None, servidor: str = None) -> None:
    """Grava por MESCLAGEM: mensagens/tutoria_encerrada vão para a conversa (a de
    `conversa_id`, ou a ativa da rota); plano/historico_planos para o slot da rota;
    metricas_superadas para o jogador. O sentinela _MANTER deixa o campo intacto, então
    cada escritor mexe só no que é seu (quem salva a conversa não apaga o plano e vice-versa).

    Proteção anti-clobber do histórico: NUNCA encolhe uma conversa já salva (um estado em
    memória vazio/transitório não pode sobrescrever a conversa real)."""
    jogador = _chave(game_name, tag_line)
    with _conectar() as con:
        _garantir_jogador(con, user_id, jogador, rota=rota, servidor=servidor)
        reg = con.execute("SELECT rota_atual FROM jogadores WHERE user_id=? AND jogador=?",
                          (user_id, jogador)).fetchone()
        alvo = rota or (reg["rota_atual"] if reg else None)

        if metricas_superadas is not _MANTER:
            con.execute("UPDATE jogadores SET metricas_superadas=? WHERE user_id=? AND jogador=?",
                        (json.dumps(metricas_superadas or {}, ensure_ascii=False),
                         user_id, jogador))

        if alvo and (plano is not _MANTER or historico_planos is not _MANTER):
            _garantir_rota(con, user_id, jogador, alvo)
            if plano is not _MANTER:
                con.execute("UPDATE rotas SET plano=? WHERE user_id=? AND jogador=? AND rota=?",
                            (json.dumps(plano, ensure_ascii=False) if plano else None,
                             user_id, jogador, alvo))
            if historico_planos is not _MANTER:
                con.execute(
                    "UPDATE rotas SET historico_planos=? WHERE user_id=? AND jogador=? AND rota=?",
                    (json.dumps(list(historico_planos or []), ensure_ascii=False),
                     user_id, jogador, alvo))

        if alvo and (mensagens is not _MANTER or tutoria_encerrada is not _MANTER):
            cid = conversa_id or _garantir_conversa_ativa(con, user_id, jogador, alvo)
            conv = con.execute("SELECT * FROM conversas WHERE id=? AND user_id=?",
                               (cid, user_id)).fetchone()
            if conv:
                if mensagens is not _MANTER:
                    antigas = json.loads(conv["mensagens"] or "[]")
                    # só sobrescreve se não encolher (igual/maior ok); senão preserva.
                    novas = list(mensagens) if len(mensagens) >= len(antigas) else antigas
                    titulo = conv["titulo"] or _titulo_automatico(novas)
                    con.execute(
                        "UPDATE conversas SET mensagens=?, titulo=?, atualizado_em=? WHERE id=?",
                        (json.dumps(novas, ensure_ascii=False), titulo, _agora(), cid))
                if tutoria_encerrada is not _MANTER:
                    con.execute("UPDATE conversas SET tutoria_encerrada=? WHERE id=?",
                                (int(bool(tutoria_encerrada)), cid))


def limpar_sessao(user_id: int, game_name: str, tag_line: str) -> None:
    """Apaga TODO o registro do jogador PARA ESTE USUÁRIO (todas as rotas e conversas).

    Casa pela chave CANÔNICA: registros legados (ex.: migrados do sessoes_tutor.json,
    que inseria a chave crua) podem estar gravados com espaços/caixa divergentes —
    "dogla la dogla #br1" e "dogla la dogla#br1" são o mesmo jogador."""
    alvo = _chave(game_name, tag_line)
    with _conectar() as con:
        rows = con.execute("SELECT jogador FROM jogadores WHERE user_id=?",
                           (user_id,)).fetchall()
        chaves = {r["jogador"] for r in rows
                  if "#" in r["jogador"] and _chave(*r["jogador"].rsplit("#", 1)) == alvo}
        chaves.add(alvo)
        for jogador in chaves:
            con.execute("DELETE FROM conversas WHERE user_id=? AND jogador=?", (user_id, jogador))
            con.execute("DELETE FROM rotas WHERE user_id=? AND jogador=?", (user_id, jogador))
            con.execute("DELETE FROM jogadores WHERE user_id=? AND jogador=?", (user_id, jogador))


# ---------------------------------------------------------------------------
# Conversas salvas (a UI usa uma por slot; várias ficam para uso futuro)
# ---------------------------------------------------------------------------

def listar_conversas(user_id: int, game_name: str, tag_line: str, rota: str) -> list[dict]:
    """Conversas do slot, mais recente primeiro: {id, titulo, criado_em, atualizado_em,
    n_mensagens, ativa}."""
    jogador = _chave(game_name, tag_line)
    with _conectar() as con:
        slot = con.execute("SELECT conversa_ativa FROM rotas WHERE user_id=? AND jogador=? AND rota=?",
                           (user_id, jogador, rota)).fetchone()
        ativa = slot["conversa_ativa"] if slot else None
        rows = con.execute(
            "SELECT id, titulo, mensagens, criado_em, atualizado_em FROM conversas"
            " WHERE user_id=? AND jogador=? AND rota=? ORDER BY atualizado_em DESC, id DESC",
            (user_id, jogador, rota)).fetchall()
    return [{"id": r["id"],
             "titulo": r["titulo"] or f"Conversa de {(r['criado_em'] or '')[:10]}",
             "criado_em": r["criado_em"], "atualizado_em": r["atualizado_em"],
             "n_mensagens": len(json.loads(r["mensagens"] or "[]")),
             "ativa": r["id"] == ativa} for r in rows]


def nova_conversa(user_id: int, game_name: str, tag_line: str, rota: str) -> int:
    """Cria uma conversa vazia no slot e a torna ativa. Devolve o id."""
    jogador = _chave(game_name, tag_line)
    with _conectar() as con:
        _garantir_jogador(con, user_id, jogador)
        _garantir_rota(con, user_id, jogador, rota)
        novo = con.execute(
            "INSERT INTO conversas (user_id, jogador, rota, criado_em, atualizado_em)"
            " VALUES (?,?,?,?,?) RETURNING id",
            (user_id, jogador, rota, _agora(), _agora())).fetchone()
        con.execute("UPDATE rotas SET conversa_ativa=? WHERE user_id=? AND jogador=? AND rota=?",
                    (novo["id"], user_id, jogador, rota))
        return novo["id"]


def selecionar_conversa(user_id: int, game_name: str, tag_line: str, rota: str,
                        conversa_id: int) -> None:
    """Torna `conversa_id` a conversa ativa do slot (ignora ids de outros usuários)."""
    jogador = _chave(game_name, tag_line)
    with _conectar() as con:
        ok = con.execute(
            "SELECT 1 FROM conversas WHERE id=? AND user_id=? AND jogador=? AND rota=?",
            (conversa_id, user_id, jogador, rota)).fetchone()
        if ok:
            _garantir_rota(con, user_id, jogador, rota)
            con.execute("UPDATE rotas SET conversa_ativa=? WHERE user_id=? AND jogador=? AND rota=?",
                        (conversa_id, user_id, jogador, rota))


def excluir_conversa(user_id: int, conversa_id: int) -> None:
    """Apaga uma conversa salva. Se era a ativa, promove a mais recente restante (ou nenhuma)."""
    with _conectar() as con:
        conv = con.execute("SELECT * FROM conversas WHERE id=? AND user_id=?",
                           (conversa_id, user_id)).fetchone()
        if not conv:
            return
        con.execute("DELETE FROM conversas WHERE id=?", (conversa_id,))
        slot = con.execute("SELECT conversa_ativa FROM rotas WHERE user_id=? AND jogador=? AND rota=?",
                           (user_id, conv["jogador"], conv["rota"])).fetchone()
        if slot and slot["conversa_ativa"] == conversa_id:
            resto = con.execute(
                "SELECT id FROM conversas WHERE user_id=? AND jogador=? AND rota=?"
                " ORDER BY atualizado_em DESC, id DESC LIMIT 1",
                (user_id, conv["jogador"], conv["rota"])).fetchone()
            con.execute("UPDATE rotas SET conversa_ativa=? WHERE user_id=? AND jogador=? AND rota=?",
                        (resto["id"] if resto else None, user_id, conv["jogador"], conv["rota"]))


def excluir_usuario(user_id: int) -> None:
    """Apaga a CONTA e todos os dados associados (LGPD art. 18: eliminação): conversas,
    rotas, jogadores, sessões de login e o próprio usuário. Definitivo e imediato."""
    with _conectar() as con:
        for tabela in ("conversas", "rotas", "jogadores", "sessoes_auth"):
            con.execute(f"DELETE FROM {tabela} WHERE user_id=?", (user_id,))
        con.execute("DELETE FROM usuarios WHERE id=?", (user_id,))


def listar_jogadores(user_id: int) -> list[dict]:
    """Análises salvas do usuário (para retomar na tela de busca): {jogador, rota_atual,
    servidor, atualizado_em}, mais recente primeiro."""
    with _conectar() as con:
        rows = con.execute(
            "SELECT jogador, rota_atual, servidor, atualizado_em FROM jogadores"
            " WHERE user_id=? ORDER BY atualizado_em DESC", (user_id,)).fetchall()
    return [dict(r) for r in rows]
