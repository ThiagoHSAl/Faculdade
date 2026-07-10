"""Compõe o logo do EloRise (assets/logo.svg): emblema hextech + monograma 'ER'
em serifa elegante (Noto Serif Display Bold), convertido para contornos SVG
auto-contidos, com brilho dourado e leve sombra; e um swoosh dourado ('subir de elo').

Regenera o logo a partir da fonte. Requer: fonttools.
Uso: python assets/gerar_monograma.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
TARGET_CAP = 46.0          # altura da maiúscula no viewBox 0..120
GAP = 7.0                  # espaço entre E e R
BASE_Y = 60.0 + TARGET_CAP / 2   # centraliza verticalmente no emblema

font = TTFont(FONT)
glyphset = font.getGlyphSet()
cmap = font.getBestCmap()


def bounds(ch):
    pen = BoundsPen(glyphset)
    glyphset[cmap[ord(ch)]].draw(pen)
    return pen.bounds  # (xMin, yMin, xMax, yMax)


_, _, _, _ = (0, 0, 0, 0)
ex0, ey0, ex1, ey1 = bounds("E")
s = TARGET_CAP / (ey1 - ey0)


def ink_w(ch):
    x0, _, x1, _ = bounds(ch)
    return (x1 - x0) * s


def path_d(ch, pen_x):
    x0, *_ = bounds(ch)
    tx = pen_x - x0 * s
    spen = SVGPathPen(glyphset)
    glyphset[cmap[ord(ch)]].draw(TransformPen(spen, (s, 0, 0, -s, tx, BASE_Y)))
    return spen.getCommands()


total = ink_w("E") + GAP + ink_w("R")
start = (120 - total) / 2
d_e = path_d("E", start)
d_r = path_d("R", start + ink_w("E") + GAP)

SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="EloRise">
  <defs>
    <linearGradient id="er-gold" gradientUnits="userSpaceOnUse" x1="60" y1="18" x2="60" y2="100">
      <stop offset="0" stop-color="#F0E6D2"/><stop offset="0.55" stop-color="#C8AA6E"/><stop offset="1" stop-color="#785A28"/>
    </linearGradient>
    <radialGradient id="er-core" cx="50%" cy="42%" r="60%">
      <stop offset="0" stop-color="#15314A"/><stop offset="1" stop-color="#0A1320"/>
    </radialGradient>
    <linearGradient id="er-face" gradientUnits="userSpaceOnUse" x1="60" y1="36" x2="60" y2="84">
      <stop offset="0" stop-color="#F6E6B8"/><stop offset="0.5" stop-color="#D3AE63"/><stop offset="1" stop-color="#9C7733"/>
    </linearGradient>
    <filter id="er-shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="1.1" stdDeviation="1.1" flood-color="#05080C" flood-opacity="0.55"/>
    </filter>
  </defs>

  <!-- Emblema hextech -->
  <polygon points="60,5 108,32.5 108,87.5 60,115 12,87.5 12,32.5" fill="url(#er-core)" stroke="url(#er-gold)" stroke-width="3.2"/>

  <!-- "Subir de elo": swoosh dourado sutil -->
  <g fill="none" stroke-linecap="round">
    <path d="M32 92 Q58 99 92 70" stroke="#2a200f" stroke-width="2.8" opacity="0.5" transform="translate(0,1.2)"/>
    <path d="M32 92 Q58 99 92 70" stroke="url(#er-face)" stroke-width="2.2"/>
  </g>
  <circle cx="92" cy="70" r="3.1" fill="url(#er-face)" stroke="#6e521f" stroke-width="0.5"/>

  <!-- Monograma "ER" em serifa, com brilho e leve sombra -->
  <g filter="url(#er-shadow)">
    <g fill="url(#er-face)" stroke="#6B4F22" stroke-width="0.5" fill-rule="evenodd">
      <path d="{d_e}"/>
      <path d="{d_r}"/>
    </g>
  </g>
</svg>
'''

out = os.path.join(os.path.dirname(__file__), "logo.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write(SVG)
print("Gerado:", out)
