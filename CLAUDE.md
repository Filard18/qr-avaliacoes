# Plaquinhas de avaliação (QR/NFC)

Redirecionador de QR code para páginas de avaliação do Google.
Cada plaquinha tem um código de 3 dígitos; o QR aponta sempre para a mesma
URL e o destino real é decidido pelo `redirects.json`. Isso permite trocar o
cliente de uma plaquinha sem reimprimir o QR.

## Dados fixos

- Repo: `Filard18/qr-avaliacoes` (público)
- URL da plaquinha: `https://filard18.github.io/qr-avaliacoes/?c=NNN`
- GitHub Pages: branch `main`, pasta raiz `/`
- Códigos existentes no JSON: `001` a `150`
- QR codes gerados: `001` a `150`, em `qrcodes/` (PNG) e `folha_qr_14mm_001-150.pdf`
- Os QRs são **limpos**: nada impresso dentro nem fora. 33 módulos, correção de
  erro M, borda de 2 módulos.
- **Quem identifica a plaquinha é a página**, não o QR: escaneando um código
  ainda não configurado, o `index.html` mostra o número em letra grande. Foi a
  escolha dele em 17/09/2026, melhor que o rótulo dentro do QR — que em 14 mm
  ficaria com 1 mm de altura.
- Tamanho de impressão: **14 mm** de lado. O piso medido é 13 mm (abaixo disso
  falha em impressão de baixa qualidade); 14 mm dá margem. Nunca reduzir abaixo
  de 13 mm com esta URL.

## Ativar uma plaquinha

Quando o usuário mandar código + cliente + URL do Google, ex.:

    001, Salão da Bianca, https://g.page/r/XXXXX/review
    plaquinha 7 pra Pizzaria Pepizza, link https://...

1. Normalizar o código para 3 dígitos (`7` -> `007`)
2. `git pull` neste repo
3. Editar `redirects.json`:

       "001": { "cliente": "Salão da Bianca", "url": "https://g.page/r/XXXXX/review" }

   Se a chave não existir, criar.
4. Commit `Ativa plaquinha <codigo> - <cliente>` e push para `main`
5. Confirmar em 1 linha: código, cliente, no ar em ~1 min

Se os 3 dados vierem completos, executar direto sem pedir confirmação.
Se faltar algum, perguntar só o que falta.

## O campo `url` aceita qualquer link

Não tem nada de Google embutido: o `index.html` só manda o celular para o que
estiver no campo `url`. Serve para avaliação do Google, site do cliente,
`wa.me`, Instagram, iFood, cardápio em PDF. A mesma plaquinha física pode
mudar de finalidade só editando o JSON.

Única exigência: a URL tem que começar com `https://`. Sem o protocolo,
`location.replace` trata como caminho relativo e o redirecionamento quebra.

## Cuidados

- Os arquivos precisam se chamar exatamente `index.html` e `redirects.json`
  na raiz. Nome diferente = site 404. (Já quebrou uma vez por isso.)
- O push só propaga no Pages depois de ~1 min.
- Não renomear o repo nem a conta: a URL está gravada dentro dos QRs já
  impressos. Mudar qualquer uma das duas invalida as plaquinhas físicas.
- Teste de site no ar: abrir `?c=` de um código vazio deve mostrar
  "Código não configurado ainda.".
- `*.github.io` é bloqueado pelo proxy do ambiente remoto do Claude Code;
  não é possível testar a URL daqui, só pelo navegador do usuário.
- Ao validar QR gerado, usar `pyzbar` (precisa de `libzbar0` via apt). O
  `cv2.QRCodeDetector` dá falso negativo e acusa falha em QR perfeito.
- O limite de um QR pequeno é o tamanho do módulo em mm, por causa do
  espalhamento de tinta — não a resolução da câmera, que sobra em qualquer
  celular atual. Abaixo de ~0,35 mm por módulo começa a falhar em impressão
  ruim. Ao testar, simular espalhamento em mm e reamostrar na resolução que o
  celular resolve; medir só em imagem digital perfeita engana.
- Para descer abaixo de 13 mm seria preciso encurtar a URL: renomear o repo
  para um nome curto e codificar em maiúscula sem `https://` (vira modo
  alfanumérico, 25 módulos), ou apontar `owen.com.br` para o Pages
  (`OWEN.COM.BR/Q/1` = 21 módulos, o mínimo de um QR). Nada disso foi feito.

## Notion — controle de vendas

Espelho do `redirects.json` para controle comercial. O GitHub continua sendo a
fonte da verdade do destino de cada plaquinha; o Notion guarda o lado de venda.

- Central: `Plaquinhas QR — Central`
  https://app.notion.com/p/3decd23a97d48100bfbfd2944ad7054e
- Banco `Controle de Plaquinhas` (150 linhas, 001 a 150)
  https://app.notion.com/p/a74067e679374cea8aa7cd926f44c109
- `database_id`: `a74067e679374cea8aa7cd926f44c109`
- `data_source_id`: `1ed99f63-5b07-4769-9061-cf088c6ffe17`
- Páginas filhas: `Passo a passo: vender e configurar`, `Problemas e soluções`

Workspace "Espaço de André Maciel". Criadas como página privada porque ele
pediu que não fossem para a aba de clientes do Owen V2; depois ele mesmo moveu
a Central para lá (hoje é uma linha do banco `Clientes`, em `Owen V2/Clientes`,
com Status "Piloto"). Não mover de volta: a escolha é dele.

### Quem manda em cada campo

| Campo | Fonte da verdade |
| --- | --- |
| `Cliente`, `URL destino`, `Configurado no GitHub` | GitHub (`redirects.json`) |
| `Status`, `Valor`, `Data da venda`, `Telefone`, `Observações` | Notion (editado à mão) |

Exceção: um código que ganha destino no JSON e ainda está `Livre` vira
`Vendida`, e a data da venda é preenchida se estiver vazia. Fora disso o sync
nunca sobrescreve dado de venda.

`Link da plaquinha` é fórmula no Notion, calculada a partir do `Código`.
Não preencher à mão.

### Ao ativar uma plaquinha

Depois do push no `redirects.json`, atualizar a linha do código no Notion
(`Cliente`, `URL destino`, `Configurado no GitHub`, `Status`) — a não ser que
o sync automático já esteja ligado, e aí o GitHub Actions faz isso.

### Sync automático (GitHub Actions)

`.github/workflows/sync-notion.yml` roda `scripts/sync_notion.py` a cada push
que altera o `redirects.json`. Sem o segredo `NOTION_TOKEN` o script só avisa e
sai com sucesso, sem falhar o workflow.

Para ligar, o usuário precisa fazer 3 coisas (Claude não consegue, envolve
credencial dele):
1. Criar uma integração interna em https://www.notion.so/profile/integrations
   e copiar o token (`ntn_...`)
2. Em Settings → Secrets and variables → Actions do repositório, criar o
   segredo `NOTION_TOKEN` com esse valor
3. Na página `Controle de Plaquinhas`, menu `...` → `Connections` → adicionar
   a integração criada

O `NOTION_DATABASE_ID` já vem com valor padrão no workflow; só precisa de
variável de repositório se o banco for trocado.

## Manter o Notion atualizado

Ele autorizou (17/09/2026) adicionar ao Notion, sem precisar perguntar a cada
vez, toda informação nova que for importante ou pertinente para a operação.

Vale para: mudança de estado (o que está no ar, o que foi validado, quantos
códigos existem, quantos foram impressos), decisão tomada, procedimento novo,
e armadilha descoberta.

Não vale para: detalhe técnico que só serve para quem mexe no código (fica
neste arquivo), nem rascunho ou hipótese ainda não confirmada.

Ao mexer no Notion, corrigir o que ficou velho em vez de empilhar seção nova:
informação desatualizada em runbook é pior que informação ausente. Exemplo já
ocorrido: a Central afirmava que faltava ligar o sync depois de ele já estar
ligado e testado.

## A página de redirecionamento

`index.html` aceita `?c=7`, `?c=007` e `?C=007` — normaliza para 3 dígitos, e o
maiúsculo existe para permitir um QR em modo alfanumérico no futuro.

Comportamento:

| Situação | O que faz |
| --- | --- |
| destino cadastrado com `https://` | redireciona na hora |
| destino vazio | mostra o número da plaquinha em letra grande |
| destino sem `https://` | mostra "Destino inválido" em vez de quebrar |
| código fora da faixa | mostra o número e avisa |
| sem `?c=` | "Link incompleto" |

O número é pintado antes do `fetch`, direto do parâmetro da URL, para aparecer
mesmo com internet ruim — é assim que ele identifica a plaquinha na mão.

Validado em Chromium via Playwright, 8 casos (`executable_path` em
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`; o caminho sem versão não
existe).
