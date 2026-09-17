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
        ERROS.append("%s: deveria ser um objeto com cliente e url" % onde)
        continue
    sobrando = set(reg) - {"cliente", "url"}
    if sobrando:
        AVISOS.append("%s: campo desconhecido %s" % (onde, ", ".join(sorted(sobrando))))
    url = (reg.get("url") or "").strip()
    if url:
        if not url.startswith("https://") and not url.startswith("http://"):
            ERROS.append("%s: a url tem que comecar com https:// (esta: %r)" % (onde, url[:60]))
        if " " in url:
            ERROS.append("%s: a url tem espaco dentro" % onde)
        vistos_url.setdefault(url, []).append(cod)
    elif (reg.get("cliente") or "").strip():
        AVISOS.append("%s: tem cliente mas nao tem url - plaquinha nao funciona ainda" % onde)

for url, codigos in vistos_url.items():
    if len(codigos) > 1:
        ERROS.append("mesmo destino em mais de uma plaquinha (%s): %s"
                     % (", ".join(codigos), url[:60]))

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
