#!/usr/bin/env python3
"""Confere o redirects.json antes que um erro derrube todas as plaquinhas.

Uma virgula faltando no JSON nao quebra uma plaquinha: quebra TODAS de uma vez,
porque o arquivo inteiro deixa de ser lido. Este script roda a cada push e
falha alto, para o aviso chegar por e-mail em menos de um minuto.
"""
import json, re, sys

ERROS, AVISOS = [], []

try:
    bruto = open("redirects.json", encoding="utf-8").read()
    dados = json.loads(bruto)
except FileNotFoundError:
    sys.exit("ERRO FATAL: redirects.json nao existe. Todas as plaquinhas estao fora do ar.")
except json.JSONDecodeError as e:
    sys.exit("ERRO FATAL: redirects.json invalido na linha %d, coluna %d: %s\n"
             "Todas as plaquinhas estao fora do ar ate isso ser corrigido.\n"
             "Normalmente e virgula sobrando ou faltando, ou aspas nao fechadas."
             % (e.lineno, e.colno, e.msg))

if not isinstance(dados, dict):
    sys.exit("ERRO FATAL: o redirects.json tem que ser um objeto {codigo: {...}}.")

vistos_url = {}
for cod, reg in dados.items():
    onde = "codigo %s" % cod
    if not re.fullmatch(r"\d{3}", cod):
        ERROS.append("%s: o codigo tem que ter exatamente 3 digitos" % onde)
    if not isinstance(reg, dict):
        ERROS.append("%s: deveria ser um objeto com o campo url" % onde)
        continue
    if "cliente" in reg:
        # este arquivo e publico: nome de cliente aqui entrega a carteira
        ERROS.append("%s: nome de cliente nao entra neste arquivo, que e publico. "
                     "O nome vive no Notion" % onde)
    sobrando = set(reg) - {"url"}
    if sobrando:
        AVISOS.append("%s: campo desconhecido %s" % (onde, ", ".join(sorted(sobrando))))
    url = (reg.get("url") or "").strip()
    if url:
        if not url.startswith("https://") and not url.startswith("http://"):
            ERROS.append("%s: a url tem que comecar com https:// (esta: %r)" % (onde, url[:60]))
        if " " in url:
            ERROS.append("%s: a url tem espaco dentro" % onde)
        vistos_url.setdefault(url, []).append(cod)


# Destino repetido quase sempre e engano grave: a plaquinha de um cliente passa
# a apontar para a de outro, e nada avisa. Mas um mesmo cliente com duas
# plaquinhas em pontos diferentes da loja e caso real, entao o grupo precisa
# estar declarado. O arquivo de grupos guarda so codigos, nunca nome de cliente.
GRUPOS = []
try:
    _g = json.load(open("grupos_compartilhados.json", encoding="utf-8"))
    if not isinstance(_g, dict):
        ERROS.append("grupos_compartilhados.json: o conteudo tem que ser um objeto "
                     '{"grupos": [["002","005"]]}')
    elif not isinstance(_g.get("grupos", []), list):
        ERROS.append('grupos_compartilhados.json: "grupos" tem que ser uma lista de listas')
    else:
        for _item in _g.get("grupos", []):
            if isinstance(_item, list) and all(isinstance(c, str) for c in _item):
                GRUPOS.append(set(_item))
            else:
                ERROS.append("grupos_compartilhados.json: cada grupo tem que ser uma lista "
                             'de codigos em texto, como ["002","005"] (achei %r)' % (_item,))
except FileNotFoundError:
    pass
except json.JSONDecodeError as e:
    ERROS.append("grupos_compartilhados.json invalido na linha %d, coluna %d: %s"
                 % (e.lineno, e.colno, e.msg))

ja_agrupado = {}
for i, grupo in enumerate(GRUPOS, 1):
    if len(grupo) < 2:
        ERROS.append("grupos_compartilhados.json: o grupo %d tem menos de 2 codigos" % i)
    for c in sorted(grupo):
        if not re.fullmatch(r"\d{3}", c):
            ERROS.append("grupos_compartilhados.json: codigo invalido %r" % c)
        elif c not in dados:
            ERROS.append("grupos_compartilhados.json: o codigo %s nao existe no redirects.json" % c)
        if c in ja_agrupado:
            ERROS.append("grupos_compartilhados.json: o codigo %s aparece em dois grupos" % c)
        ja_agrupado[c] = i
    # plaquinhas do mesmo cliente que apontam para lugares diferentes: ou uma
    # delas foi configurada errada, ou o grupo nao deveria existir
    destinos = {(dados.get(c, {}).get("url") or "").strip() for c in grupo}
    destinos.discard("")
    if len(destinos) > 1:
        AVISOS.append("grupo %d (%s) tem destinos diferentes entre si" % (i, ", ".join(sorted(grupo))))

for url, codigos in vistos_url.items():
    if len(codigos) < 2:
        continue
    conjunto = set(codigos)
    if any(conjunto <= grupo for grupo in GRUPOS):
        print("compartilhado (declarado): %s -> %s" % (", ".join(sorted(conjunto)), url[:50]))
        continue
    ERROS.append("mesmo destino em mais de uma plaquinha (%s): %s\n"
                 "    Se for o mesmo cliente com mais de uma plaquinha, declare o grupo em "
                 "grupos_compartilhados.json. Se nao for, uma delas esta apontando para o "
                 "cliente errado." % (", ".join(sorted(conjunto)), url[:60]))

configuradas = sum(1 for r in dados.values() if (r.get("url") or "").strip())
print("codigos: %d | configuradas: %d | livres: %d"
      % (len(dados), configuradas, len(dados) - configuradas))

for a in AVISOS:
    print("AVISO: " + a)
if ERROS:
    print("\n%d erro(s):" % len(ERROS))
    for e in ERROS:
        print("  - " + e)
    sys.exit(1)
print("redirects.json OK")
