"""Folha de prova dos QRs para o fornecedor das placas 3D.

Uma folha A4 com os QR codes no tamanho REAL de impressao (32 mm), para o
fornecedor conferir com regua antes de produzir o lote. Traz tambem a regua de
50 mm: se ela nao medir 50 mm no papel, a folha foi impressa com escala e
nenhuma medida ali vale.
"""
import re, sys, cairosvg

# uso: python3 scripts/gera_folha_prova.py 11 30
INI = int(sys.argv[1]) if len(sys.argv) > 1 else 11
FIM = int(sys.argv[2]) if len(sys.argv) > 2 else 30
assert 1 <= INI <= FIM <= 150, "faixa fora de 001..150"
assert FIM - INI + 1 <= 20, "cabem 20 por folha; rode em faixas de ate 20"
ARQ = "folha_prova_qr_%03d-%03d" % (INI, FIM)

# A4 em mm
LARG, ALT = 210.0, 297.0
MARGEM = 14.0
COLS, LINHAS = 4, 5
QR = 32.0                      # tamanho real do QR, borda branca incluida
CELA_L = (LARG - 2 * MARGEM) / COLS
CELA_A = 45.0
TOPO = 60.0                    # onde comeca a grade

FONTE = "DejaVu Sans, Helvetica, Arial, sans-serif"


def modulos(cod):
    """Le os <rect> do SVG daquele codigo, em mm, relativos a 32x32."""
    svg = open(f"qrcodes_svg/{cod}.svg", encoding="utf-8").read()
    fora = []
    for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg):
        fora.append(tuple(float(g) for g in m.groups()))
    return fora


p = []
a = p.append
a(f'<?xml version="1.0" encoding="UTF-8"?>')
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARG}mm" height="{ALT}mm" '
  f'viewBox="0 0 {LARG} {ALT}">')
a(f'<rect width="{LARG}" height="{ALT}" fill="#ffffff"/>')
a(f'<g font-family="{FONTE}">')

# ---- cabecalho
a(f'<text x="{MARGEM}" y="18" font-size="6.2" font-weight="700">'
  f'FOLHA DE PROVA — QR CODES 011 a 030</text>')
a(f'<text x="{MARGEM}" y="24.5" font-size="3.4" fill="#444">'
  f'Placas NFC + QR · Owen · 20 peças · cada QR é único e não pode repetir</text>')
a(f'<line x1="{MARGEM}" y1="28" x2="{LARG-MARGEM}" y2="28" stroke="#000" stroke-width="0.4"/>')

espec = [
    ("Tamanho do QR", "32,0 × 32,0 mm (borda branca incluída)"),
    ("Módulo (quadradinho)", "0,865 mm — mínimo do processo"),
    ("Grade", "33 módulos + 2 de borda em cada lado = 37"),
    ("Borda branca", "1,73 mm nos 4 lados — faz parte do código, não cortar"),
]
y = 34.5
for k, v in espec:
    a(f'<text x="{MARGEM}" y="{y}" font-size="3.3" font-weight="700">{k}</text>')
    a(f'<text x="{MARGEM+42}" y="{y}" font-size="3.3">{v}</text>')
    y += 4.6

# regua de conferencia: prova que a folha nao foi reescalada na impressao
rx, ry = LARG - MARGEM - 50, 34.0
a(f'<line x1="{rx}" y1="{ry}" x2="{rx+50}" y2="{ry}" stroke="#000" stroke-width="0.35"/>')
for i in range(6):
    x = rx + i * 10
    a(f'<line x1="{x}" y1="{ry-1.6}" x2="{x}" y2="{ry+1.6}" stroke="#000" stroke-width="0.35"/>')
a(f'<text x="{rx+25}" y="{ry+5.2}" font-size="3.1" text-anchor="middle" fill="#444">'
  f'confira com régua: esta barra tem 50 mm</text>')
a(f'<text x="{rx+25}" y="{ry+9.2}" font-size="3.1" text-anchor="middle" fill="#444">'
  f'se não tiver, imprima em 100% (sem "ajustar à página")</text>')

# ---- grade dos QRs
i = 0
for n in range(INI, FIM + 1):
    cod = "%03d" % n
    lin, col = divmod(i, COLS)
    cx = MARGEM + col * CELA_L + (CELA_L - QR) / 2
    cy = TOPO + lin * CELA_A
    a(f'<g transform="translate({cx:.4f},{cy:.4f})">')
    a(f'<rect width="{QR}" height="{QR}" fill="#ffffff"/>')
    a('<g fill="#000000">')
    for x, yy, w, h in modulos(cod):
        a(f'<rect x="{x}" y="{yy}" width="{w}" height="{h}"/>')
    a('</g>')
    # marca de canto: so para conferir o esquadro, fora da area do QR
    a(f'<path d="M -1.6 0 h -1.2 M 0 -1.6 v -1.2 M {QR+1.6} 0 h 1.2 M {QR} -1.6 v -1.2" '
      f'stroke="#bbb" stroke-width="0.25" fill="none"/>')
    a('</g>')
    a(f'<text x="{cx+QR/2}" y="{cy+QR+6.2}" font-size="5.4" font-weight="700" '
      f'text-anchor="middle">{cod}</text>')
    a(f'<text x="{cx+QR/2}" y="{cy+QR+10.2}" font-size="2.5" text-anchor="middle" '
      f'fill="#666">?c={cod}</text>')
    i += 1

# ---- rodape
fy = TOPO + LINHAS * CELA_A + 4
a(f'<line x1="{MARGEM}" y1="{fy}" x2="{LARG-MARGEM}" y2="{fy}" stroke="#000" stroke-width="0.4"/>')
a(f'<text x="{MARGEM}" y="{fy+6}" font-size="3.6" font-weight="700">'
  f'IMPORTANTE — impressão 3D com a face para baixo</text>')
a(f'<text x="{MARGEM}" y="{fy+11}" font-size="3.2">'
  f'Nesta folha os QRs estão na leitura correta. Se a peça for impressa com a face para baixo, '
  f'o arquivo de corte precisa</text>')
a(f'<text x="{MARGEM}" y="{fy+15.2}" font-size="3.2">'
  f'ser <tspan font-weight="700">espelhado no eixo X</tspan>. Sem isso a peça sai invertida e '
  f'nenhum celular lê o código.</text>')
a(f'<text x="{MARGEM}" y="{fy+21.5}" font-size="3.2">'
  f'<tspan font-weight="700">Cada número é um código diferente.</tspan> '
  f'Trocar a ordem ou repetir um QR faz duas lojas receberem a mesma peça.</text>')
a(f'<text x="{MARGEM}" y="{fy+27.5}" font-size="2.8" fill="#666">'
  f'Arquivos vetoriais para CAD: um SVG por código, 32 mm, no mesmo envio.</text>')

a('</g></svg>')
svg = "\n".join(p)
open(f"{ARQ}.svg", "w", encoding="utf-8").write(svg)
cairosvg.svg2pdf(bytestring=svg.encode(), write_to=f"{ARQ}.pdf")
print("gerado:", ARQ + ".pdf")
