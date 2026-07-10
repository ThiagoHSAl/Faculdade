"""Gera o favicon do EloRise (assets/icon.png) renderizando o assets/logo.svg —
assim a aba do navegador usa exatamente a mesma arte do logo. Requer: cairosvg.

Regenere o logo antes (python assets/gerar_monograma.py).
Uso: python assets/gerar_icone.py
"""
import os
import cairosvg

AQUI = os.path.dirname(__file__)
cairosvg.svg2png(
    url=os.path.join(AQUI, "logo.svg"),
    write_to=os.path.join(AQUI, "icon.png"),
    output_width=256,
    output_height=256,            # fundo transparente fora do hexágono
)
print("Gerado:", os.path.join(AQUI, "icon.png"))
