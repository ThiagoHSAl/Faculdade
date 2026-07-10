"""
viz_partidas.py — Fase 1 do módulo "Análise de Partidas": mapa de mortes.

Plota as mortes do jogador sobre o minimapa da Fenda do Invocador. Cada marcador
é o ÍCONE DO CAMPEÃO do jogador naquela partida, em PRETO E BRANCO (recortado em
círculo, com um anel vermelho sinalizando a morte), posicionado na coordenada
exata do evento de morte.

Assets (minimapa do Data Dragon `img/map/map11.png` e ícone do campeão) são
baixados uma vez e cacheados em disco; a imagem composta é gerada com Pillow.

Coordenadas: a textura map11 do Data Dragon cobre o jogo de ~-120 a ~14870 em x/y
(origem no canto inferior-esquerdo), então invertemos o eixo y ao converter para
pixel da imagem (cujo (0,0) é o canto superior-esquerdo).
"""

import io
from pathlib import Path

import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

_DDRAGON = "https://ddragon.leagueoflegends.com/cdn"
_ASSETS_DIR = Path(__file__).resolve().parent / "cache_partidas" / "assets"
_TIMEOUT = 15

# Limites de coordenada de jogo cobertos pela textura map11 do Data Dragon.
_COORD_MIN = -120
_COORD_MAX = 14870

_VERMELHO = (224, 107, 107, 255)  # mesma paleta do app (--red)


def _baixar(url: str, destino: Path) -> Path | None:
    """Baixa `url` para `destino` (cache em disco). Devolve o caminho ou None em falha."""
    if destino.exists():
        return destino
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        _ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(resp.content)
        return destino
    except (requests.RequestException, OSError):
        return None


def mapa_base(versao: str) -> Image.Image | None:
    """Minimapa da Fenda do Invocador (map11) como imagem RGBA, cacheado em disco."""
    destino = _ASSETS_DIR / f"map11_{versao}.png"
    caminho = _baixar(f"{_DDRAGON}/{versao}/img/map/map11.png", destino)
    if caminho is None:
        return None
    try:
        return Image.open(caminho).convert("RGBA")
    except OSError:
        return None


def _icone_pb(icone_url: str, tamanho: int) -> Image.Image | None:
    """Ícone do campeão em preto e branco, recortado em círculo, com anel vermelho."""
    # nome de arquivo de cache estável a partir da URL (último segmento)
    nome = icone_url.rsplit("/", 1)[-1] or "campeao.png"
    caminho = _baixar(icone_url, _ASSETS_DIR / nome)
    if caminho is None:
        return None
    try:
        base = Image.open(caminho).convert("RGB")
    except OSError:
        return None

    # preto e branco, redimensionado
    pb = ImageOps.grayscale(base).convert("RGBA").resize((tamanho, tamanho))

    # máscara circular
    mascara = Image.new("L", (tamanho, tamanho), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, tamanho - 1, tamanho - 1), fill=255)
    out = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    out.paste(pb, (0, 0), mascara)

    # anel vermelho (sinaliza morte)
    anel = max(2, tamanho // 12)
    ImageDraw.Draw(out).ellipse(
        (anel // 2, anel // 2, tamanho - anel // 2 - 1, tamanho - anel // 2 - 1),
        outline=_VERMELHO, width=anel,
    )
    return out


def _fonte(tamanho: int) -> ImageFont.ImageFont:
    """Fonte para os rótulos de minuto (com fallback se `size` não for suportado)."""
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def _rotulo_minuto(desenho: ImageDraw.ImageDraw, px: int, py: int,
                   t_s: int, tamanho_icone: int) -> None:
    """Escreve o minuto da morte (ex.: "12'") logo abaixo do marcador, com fundo escuro."""
    txt = f"{t_s // 60}'"
    fonte = _fonte(max(11, tamanho_icone // 2))
    bbox = desenho.textbbox((0, 0), txt, font=fonte)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    lx, ly = px - tw // 2, py + tamanho_icone // 2 - 1
    desenho.rectangle((lx - 3, ly - 2, lx + tw + 3, ly + th + 4),
                      fill=(7, 13, 20, 235))
    desenho.text((lx, ly), txt, fill=(240, 230, 210, 255), font=fonte)


def _para_pixel(x: int, y: int, w: int, h: int) -> tuple[int, int]:
    span = _COORD_MAX - _COORD_MIN
    px = int((x - _COORD_MIN) / span * w)
    py = int(h - (y - _COORD_MIN) / span * h)  # eixo y invertido
    return max(0, min(w - 1, px)), max(0, min(h - 1, py))


def coord_pixel(x: int, y: int, w: int, h: int) -> tuple[int, int]:
    """Converte coordenada de jogo (x, y) em pixel da imagem `w`x`h` (público)."""
    return _para_pixel(x, y, w, h)


def base_e_pixels(pontos: list[dict], versao: str) -> tuple[Image.Image | None, list[tuple]]:
    """Minimapa limpo (sem marcadores) + a posição EM PIXEL de cada ponto.

    Cada item de `pontos` precisa ter x, y (formato da timeline normalizada).
    Retorna `(imagem, [(px, py, ponto), ...])`. Base genérica para o heatmap de
    posicionamento (Fase 3) e qualquer outra camada sobre o mapa.
    """
    base = mapa_base(versao)
    if base is None:
        return None, []
    w, h = base.size
    pix = []
    for p in pontos:
        x, y = p.get("x"), p.get("y")
        if x is None or y is None:
            continue
        px, py = _para_pixel(x, y, w, h)
        pix.append((px, py, p))
    return base, pix


def mapa_e_pontos(mortes: list[dict], icone_url: str, versao: str,
                  tamanho_icone: int = 38) -> tuple[Image.Image | None, list[dict]]:
    """
    Compõe o minimapa com um ícone P&B do campeão por morte e devolve também a
    posição EM PIXEL de cada marcador — para sobrepor uma camada interativa
    (hover) por cima da imagem.

    Retorna `(imagem_RGBA, pontos)`, onde cada ponto é
    `{"px", "py", "morte"}`. Mortes sem coordenada são ignoradas. `imagem` é None
    se o minimapa falhar ao carregar.
    """
    base = mapa_base(versao)
    if base is None:
        return None, []
    w, h = base.size
    icone = _icone_pb(icone_url, tamanho_icone)

    desenho = ImageDraw.Draw(base)
    pontos = []
    for m in mortes:
        x, y = m.get("x"), m.get("y")
        if x is None or y is None:
            continue
        px, py = _para_pixel(x, y, w, h)
        if icone is not None:
            base.alpha_composite(icone, (px - tamanho_icone // 2, py - tamanho_icone // 2))
        else:
            # Fallback se o ícone do campeão não baixar: ponto vermelho.
            r = 7
            desenho.ellipse((px - r, py - r, px + r, py + r),
                            fill=_VERMELHO, outline=(255, 255, 255, 255))
        pontos.append({"px": px, "py": py, "morte": m})
    return base, pontos


def mapa_de_mortes(mortes: list[dict], icone_url: str, versao: str,
                   tamanho_icone: int = 38,
                   mostrar_minuto: bool = False) -> Image.Image | None:
    """Imagem estática do mapa de mortes. `mostrar_minuto` desenha o minuto em
    cada marcador (export estático); na UI o tempo vai no hover."""
    base, pontos = mapa_e_pontos(mortes, icone_url, versao, tamanho_icone)
    if base is None:
        return None
    if mostrar_minuto:
        desenho = ImageDraw.Draw(base)
        for pt in pontos:
            t_s = pt["morte"].get("t_s")
            if t_s is not None:
                _rotulo_minuto(desenho, pt["px"], pt["py"], t_s, tamanho_icone)
    return base


def mapa_de_mortes_png(mortes: list[dict], icone_url: str, versao: str,
                       tamanho_icone: int = 38,
                       mostrar_minuto: bool = False) -> bytes | None:
    """Igual a `mapa_de_mortes`, mas devolve PNG em bytes."""
    img = mapa_de_mortes(mortes, icone_url, versao, tamanho_icone, mostrar_minuto)
    if img is None:
        return None
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
