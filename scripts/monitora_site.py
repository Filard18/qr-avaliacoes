#!/usr/bin/env python3
"""Confere de hora em hora se as plaquinhas que estao na rua ainda funcionam.

Roda pelo GitHub Actions. Quando falha, o GitHub manda e-mail para o dono do
repositorio: e esse o alarme. Um cliente so descobre que a plaquinha quebrou
quando alguem tenta avaliar e nao consegue, e ai ja perdeu a avaliacao e a
confianca. Aqui a gente descobre antes.

Tres camadas, da mais grave para a menos:

  1. A pagina esta no ar?          cai isto, caem TODAS as plaquinhas
  2. O redirects.json esta inteiro? idem
  3. O destino de cada cliente responde?  cai isto, cai so aquela plaquinha

Falso alarme e pior que nenhum alarme, entao a camada 3 so acusa o que e
inequivoco (404, 410, dominio que sumiu). Google bloqueando o runner (403,
429) nao e problema da plaquinha e vira aviso, nao falha.
"""
import json, os, sys, time, urllib.error, urllib.request

BASE = os.environ.get("BASE_URL", "https://filard18.github.io/qr-avaliacoes/").rstrip("/") + "/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")
FALHAS, AVISOS = [], []
# esperas: o Pages leva ate ~2 min para publicar, e o Google nao gosta de rajada.
# Os testes encurtam as duas por variavel de ambiente.
ESPERA_REPUBLICACAO = float(os.environ.get("ESPERA_REPUBLICACAO", "90"))
ESPERA_ENTRE_DESTINOS = float(os.environ.get("ESPERA_ENTRE_DESTINOS", "1.5"))


def busca(url, metodo="GET", tempo=25):
    req = urllib.request.Request(url, method=metodo, headers={
        "User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=tempo) as r:
            return r.status, r.read(400000)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return None, str(e).encode()


def camada_1_a_pagina_esta_no_ar():
    status, corpo = busca(BASE + "?c=001&v=1")
    if status != 200:
        FALHAS.append("A PAGINA ESTA FORA DO AR (%s em %s). Todas as plaquinhas "
                      "da rua estao quebradas agora." % (status, BASE))
        return False
    texto = corpo.decode("utf-8", "replace")
    # marcas do index.html: se sumirem, alguem publicou outra coisa no lugar
    for marca in ('id="caixa"', "redirects.json", "location.replace"):
        if marca not in texto:
            FALHAS.append("A pagina respondeu, mas nao e o redirecionador: falta %r. "
                          "Alguem publicou outro index.html por cima." % marca)
            return False
    return True


def camada_2_o_arquivo_de_destinos(esperado):
    status, corpo = busca(BASE + "redirects.json?" + str(int(time.time())))
    if status != 200:
        FALHAS.append("O redirects.json nao carrega (%s). Todas as plaquinhas quebradas." % status)
        return None
    try:
        vivo = json.loads(corpo)
    except json.JSONDecodeError as e:
        FALHAS.append("O redirects.json publicado esta corrompido (linha %d): %s. "
                      "Todas as plaquinhas quebradas." % (e.lineno, e.msg))
        return None
    if len(vivo) != len(esperado):
        FALHAS.append("O site publicou %d codigos, o repositorio tem %d."
                      % (len(vivo), len(esperado)))
        return vivo
    # divergencia logo depois de um push e normal: o Pages leva ate 2 min
    difere = [c for c in esperado
              if (vivo.get(c) or {}).get("url", "") != esperado[c].get("url", "")]
    if difere:
        time.sleep(ESPERA_REPUBLICACAO)
        status, corpo = busca(BASE + "redirects.json?" + str(int(time.time())))
        try:
            vivo = json.loads(corpo)
        except Exception:
            FALHAS.append("O redirects.json publicado parou de carregar na reconferencia.")
            return None
        difere = [c for c in esperado
                  if (vivo.get(c) or {}).get("url", "") != esperado[c].get("url", "")]
        if difere:
            FALHAS.append("O site esta servindo uma versao velha nos codigos %s. "
                          "A publicacao do GitHub Pages falhou ou travou."
                          % ", ".join(sorted(difere)[:10]))
    return vivo


def camada_3_os_destinos(vivo):
    configuradas = sorted(c for c, r in (vivo or {}).items() if (r.get("url") or "").strip())
    print("plaquinhas configuradas: %d" % len(configuradas))
    for cod in configuradas:
        url = vivo[cod]["url"].strip()
        status, _ = busca(url, tempo=20)
        if status is None:
            status, _ = busca(url, tempo=20)          # uma segunda chance
        if status is None:
            AVISOS.append("%s: o destino nao respondeu duas vezes seguidas" % cod)
        elif status in (404, 410):
            FALHAS.append("%s: o destino sumiu (%s). O cliente perdeu a pagina de "
                          "avaliacao e a plaquinha dele leva a lugar nenhum." % (cod, status))
        elif status in (403, 429):
            AVISOS.append("%s: o Google respondeu %s ao robo (bloqueio de automacao, "
                          "nao e problema da plaquinha)" % (cod, status))
        elif status >= 500:
            AVISOS.append("%s: o destino respondeu %s, provavelmente instabilidade "
                          "passageira" % (cod, status))
        else:
            print("  %s ok (%s)" % (cod, status))
        time.sleep(ESPERA_ENTRE_DESTINOS)                                # nao martelar o Google


esperado = json.load(open("redirects.json", encoding="utf-8"))
print("conferindo %s" % BASE)
if camada_1_a_pagina_esta_no_ar():
    camada_3_os_destinos(camada_2_o_arquivo_de_destinos(esperado))

for a in AVISOS:
    print("AVISO: " + a)
if FALHAS:
    print("\n%d PROBLEMA(S) COM AS PLAQUINHAS NA RUA:" % len(FALHAS))
    for f in FALHAS:
        print("  - " + f)
    print("\nO que fazer esta em 'Problemas e solucoes', no Notion.")
    sys.exit(1)
print("\ntudo funcionando")
