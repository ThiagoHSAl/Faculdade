"""
riot_client.py — Wrapper da Riot API com tratamento de rate limit.

Encapsula todos os endpoints necessários para a Feature 1:
  - Account v1  (by-riot-id)         → PUUID
  - Summoner v4 (by-puuid)           → Summoner ID
  - League v4   (entries/by-puuid)   → Elo atual
  - Match v5    (by-puuid + match)    → Histórico de partidas
"""

import time
import requests
from config import RIOT_API_KEY, PLATFORM, REGION


# ──────────────────────────────────────────────
# Exceções customizadas
# ──────────────────────────────────────────────

class RiotAPIError(Exception):
    """Erro genérico da Riot API."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[Riot API {status_code}] {message}")


class PlayerNotFoundError(RiotAPIError):
    """Riot ID não encontrado no servidor."""
    pass


class NoMatchesFoundError(Exception):
    """Jogador não tem partidas ranqueadas recentes."""
    pass


# ──────────────────────────────────────────────
# URLs base por tipo de roteamento
# ──────────────────────────────────────────────
def _build_bases(platform: str, region: str) -> dict[str, str]:
    return {
        "account":  f"https://{region}.api.riotgames.com",
        "match":    f"https://{region}.api.riotgames.com",
        "platform": f"https://{platform}.api.riotgames.com",
    }


# ──────────────────────────────────────────────
# Cliente
# ──────────────────────────────────────────────

class RiotClient:
    """
    Wrapper fino da Riot REST API.

    Parâmetros
    ----------
    api_key  : Chave da API Riot (padrão: variável de ambiente RIOT_API_KEY)
    platform : Servidor (padrão: br1)
    region   : Roteamento regional (padrão: americas)
    """

    def __init__(
        self,
        api_key: str = RIOT_API_KEY,
        platform: str = PLATFORM,
        region: str = REGION,
    ):
        if not api_key:
            raise ValueError(
                "RIOT_API_KEY não configurada. "
                "Adicione ao arquivo .env ou passe via parâmetro."
            )
        self._headers = {"X-Riot-Token": api_key}
        self._base = _build_bases(platform, region)
        # Session com keep-alive: sem ela, cada chamada paga um handshake TCP+TLS novo
        # (a coleta faz ~40 GETs). O pool de 8 casa com o executor de generate_stats;
        # GETs concorrentes na mesma Session são seguros (urllib3 gerencia o pool).
        self._http = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=8, pool_maxsize=8)
        self._http.mount("https://", adapter)

    # ── HTTP helper ───────────────────────────────────────────────────

    def _get(self, base_key: str, path: str, params: dict | None = None) -> any:
        """
        Faz GET com retry automático em caso de rate limit (HTTP 429).
        """
        url = self._base[base_key] + path
        for attempt in range(4):
            resp = self._http.get(
                url, headers=self._headers, params=params or {}, timeout=10
            )
            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                # Respeitar o cabeçalho Retry-After se presente
                wait = int(resp.headers.get("Retry-After", 2 ** attempt))
                print(f"  ⏳ Rate limit atingido — aguardando {wait}s (tentativa {attempt+1}/4)")
                time.sleep(wait)
                continue

            if resp.status_code == 404:
                raise PlayerNotFoundError(404, f"Recurso não encontrado: {path}")

            raise RiotAPIError(resp.status_code, resp.text[:300])

        raise RiotAPIError(429, "Rate limit: tentativas esgotadas.")

    # ── Account v1 (regional) ─────────────────────────────────────────

    def get_account(self, game_name: str, tag_line: str) -> dict:
        """
        Retorna: { puuid, gameName, tagLine }

        Exemplo: get_account("Jhin Frio", "Coffe")
        """
        path = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._get("account", path)

    # ── Summoner v4 (platform) ────────────────────────────────────────

    def get_summoner_by_puuid(self, puuid: str) -> dict:
        """
        Retorna: { id (summonerId), puuid, summonerLevel, ... }
        """
        return self._get("platform", f"/lol/summoner/v4/summoners/by-puuid/{puuid}")

    # ── League v4 (platform) ──────────────────────────────────────────

    def get_ranked_entries(self, puuid: str) -> list[dict]:
        """
        Retorna lista de entradas ranqueadas (Solo/Duo, Flex, etc.).
        Cada entrada tem: queueType, tier, rank, leaguePoints, wins, losses
        """
        return self._get("platform", f"/lol/league/v4/entries/by-puuid/{puuid}")

    # ── Match v5 (regional) ───────────────────────────────────────────

    def get_match_ids(
        self,
        puuid: str,
        count: int = 20,
        queue: int | None = 420,
    ) -> list[str]:
        """
        Retorna lista de match IDs recentes.

        queue=420  → Ranked Solo/Duo
        queue=440  → Ranked Flex
        queue=400  → Normal (Draft)
        queue=None → Todas as filas ranqueadas

        Ao passar um `queue` específico NÃO enviamos `type`: o filtro por queue já
        basta, e `type=ranked` + `queue=400` (Normal, que não é ranqueada) faz a Riot
        devolver lista VAZIA. Sem queue, mantemos `type=ranked` (todas as ranqueadas).
        """
        params: dict = {"count": count}
        if queue is not None:
            params["queue"] = queue
        else:
            params["type"] = "ranked"
        path = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        return self._get("match", path, params)

    def get_match(self, match_id: str) -> dict:
        """
        Retorna os dados completos de uma partida.
        """
        return self._get("match", f"/lol/match/v5/matches/{match_id}")

    def get_match_timeline(self, match_id: str) -> dict:
        """
        Retorna a timeline da partida: frames (~1 por minuto, com posição/ouro/xp
        de cada participante) e events (mortes, objetivos, wards, placas, itens...),
        com timestamp em ms. Base do módulo de análise visual de partidas.
        """
        return self._get("match", f"/lol/match/v5/matches/{match_id}/timeline")