#!/usr/bin/env python3
"""Reescreve os SVGs dos QRs num formato que fatiador 3D importa de primeira.

O SVG antigo era desenhado para olho humano e para CAD, nao para o importador
do Bambu Studio. Ele tinha quatro coisas que atrapalham esse importador:

  1. um retangulo vermelho de contorno, sem preenchimento, so com traco.
     Forma sem preenchimento nao vira solido: ou e ignorada, ou entra como
     um quadro fino em volta do codigo.
  2. o preenchimento declarado no <g> e nao em cada forma, o que depende do
     parser herdar atributo de grupo.
  3. <title> e <desc> antes do desenho.
  4. centenas de <rect> soltos em vez de um caminho unico.

Aqui sai o minimo que todo importador entende: um <path> unico, com o
preenchimento declarado nele mesmo, sem grupo, sem metadado e sem traco.
Coordenadas absolutas em M/L/Z, que e o subconjunto mais universal do formato.

Uso: python3 scripts/gera_svg_bambu.py 36 135
"""
import re, sys, os

ENTRADA, SAIDA = "qrcodes_svg", "qrcodes_svg_bambu"
RE_RECT = re.compile(r'<rect\s+x="([\d.]+)"\s+y="([\d.]+)"\s+width="([\d.]+)"\s+height="([\d.]+)"\s*/>')


def modulos(cod):
    """So os retangulos dos modulos. O de contorno nao casa com o padrao
    porque tem id e atributos de traco antes das medidas, entao fica de fora
    por construcao, nao por sorte."""
    texto = open(f"{ENTRADA}/{cod}.svg", encoding="utf-8").read()
    corpo = texto.split('<g id="modulos"')[1].split("</g>")[0]
    return [tuple(float(g) for g in m.groups()) for m in RE_RECT.finditer(corpo)]


def caminho(rs):
    partes = []
    for x, y, w, h in rs:
        x2, y2 = round(x + w, 4), round(y + h, 4)
        x, y = round(x, 4), round(y, 4)
        partes.append(f"M{x} {y}L{x2} {y}L{x2} {y2}L{x} {y2}Z")
    return "".join(partes)


def converte(cod, lado=32.0):
    rs = modulos(cod)
    d = caminho(rs)
    x0 = min(r[0] for r in rs); y0 = min(r[1] for r in rs)
    x1 = max(r[0] + r[2] for r in rs); y1 = max(r[1] + r[3] for r in rs)
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lado}mm" height="{lado}mm" '
        f'viewBox="0 0 {lado} {lado}">\n'
        f'<path fill="#000000" fill-rule="nonzero" stroke="none" d="{d}"/>\n'
        "</svg>\n"
    )
    os.makedirs(SAIDA, exist_ok=True)
    open(f"{SAIDA}/{cod}.svg", "w", encoding="utf-8").write(svg)
    return len(rs), (x1 - x0), (y1 - y0), len(svg)


if __name__ == "__main__":
    ini = int(sys.argv[1]) if len(sys.argv) > 1 else 36
    fim = int(sys.argv[2]) if len(sys.argv) > 2 else 135
    larguras, tam = set(), 0
    for n in range(ini, fim + 1):
        cod = "%03d" % n
        q, lx, ly, b = converte(cod)
        larguras.add((round(lx, 4), round(ly, 4)))
        tam += b
    print(f"{fim-ini+1} arquivos | area escura: {larguras} mm | media {tam//(fim-ini+1)//1024} KB")
