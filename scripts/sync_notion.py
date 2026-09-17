#!/usr/bin/env python3
"""Sincroniza o redirects.json com o banco "Controle de Plaquinhas" no Notion.

Direcao unica, GitHub -> Notion, e so nos campos que o GitHub manda:
  URL destino e Configurado no GitHub.

O nome do cliente NAO passa por aqui de proposito: o redirects.json e publico,
e uma lista de clientes exposta entrega a carteira para qualquer concorrente.
O nome vive so no Notion, escrito direto por quem ativa a plaquinha.

O que o Notion manda continua intocado: Cliente, Valor, Data da venda,
Telefone, Observacoes e o Status (com uma excecao: um codigo que acabou de ganhar
destino e ainda esta "Livre" vira "Vendida", e a data da venda e preenchida
se estiver vazia). Assim a planilha de vendas nunca e sobrescrita.

Roda sem NOTION_TOKEN: apenas avisa e sai com sucesso, para nao poluir o
historico de Actions de quem ainda nao configurou o segredo.
"""
import json, os, sys, urllib.request, urllib.error
from datetime import date

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DB_ID = os.environ.get("NOTION_DATABASE_ID", "").strip()
API = "https://api.notion.com/v1"
HDR = {"Authorization": "Bearer %s" % TOKEN,
       "Notion-Version": "2022-06-28",
       "Content-Type": "application/json"}

def call(method, path, body=None):
    req = urllib.request.Request(
        API + path, method=method, headers=HDR,
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:400]
        sys.exit("ERRO Notion %s em %s %s\n%s" % (e.code, method, path, detalhe))

def titulo(prop):
    return "".join(t.get("plain_text", "") for t in (prop or {}).get("title", []))

def main():
    if not TOKEN or not DB_ID:
        print("NOTION_TOKEN ou NOTION_DATABASE_ID nao configurado - sync ignorado.")
        print("Como ligar: veja a secao Notion no CLAUDE.md deste repositorio.")
        return 0

    destinos = json.load(open("redirects.json", encoding="utf-8"))

    # todas as linhas do banco, paginado
    linhas, cursor = {}, None
    while True:
        corpo = {"page_size": 100}
        if cursor:
            corpo["start_cursor"] = cursor
        r = call("POST", "/databases/%s/query" % DB_ID, corpo)
        for pg in r["results"]:
            cod = titulo(pg["properties"].get("Código"))
            if cod:
                linhas[cod] = pg
        if not r.get("has_more"):
            break
        cursor = r["next_cursor"]
    print("linhas no Notion: %d | codigos no redirects.json: %d"
          % (len(linhas), len(destinos)))

    hoje = date.today().isoformat()
    criadas = atualizadas = 0

    for cod in sorted(destinos):
        dado = destinos[cod] or {}
        url = (dado.get("url") or "").strip()
        configurado = bool(url)

        props = {
            "URL destino": {"url": url or None},
            "Configurado no GitHub": {"checkbox": configurado},
        }

        pg = linhas.get(cod)
        if pg is None:
            # codigo novo no JSON que ainda nao existe no banco
            props["Código"] = {"title": [{"text": {"content": cod}}]}
            props["Status"] = {"select": {"name": "Vendida" if configurado else "Livre"}}
            if configurado:
                props["Data da venda"] = {"date": {"start": hoje}}
            call("POST", "/pages", {"parent": {"database_id": DB_ID}, "properties": props})
            criadas += 1
            print("  + %s criado" % cod)
            continue

        atual = pg["properties"]
        mudou = ((atual.get("URL destino", {}).get("url") or "") != url
                 or bool(atual.get("Configurado no GitHub", {}).get("checkbox")) != configurado)

        # promove a venda sem mexer em status que a pessoa ja ajustou a mao
        if configurado:
            status = (atual.get("Status", {}).get("select") or {}).get("name")
            if status in (None, "Livre"):
                props["Status"] = {"select": {"name": "Vendida"}}
                mudou = True
            if not (atual.get("Data da venda", {}).get("date") or {}).get("start"):
                props["Data da venda"] = {"date": {"start": hoje}}
                mudou = True

        if mudou:
            call("PATCH", "/pages/%s" % pg["id"], {"properties": props})
            atualizadas += 1
            print("  ~ %s atualizado" % cod)

    print("pronto: %d criadas, %d atualizadas, %d sem mudanca"
          % (criadas, atualizadas, len(destinos) - criadas - atualizadas))
    return 0

if __name__ == "__main__":
    sys.exit(main())
