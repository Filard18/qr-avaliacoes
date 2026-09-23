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
- QR codes gerados: `001` a `150`, em `qrcodes_svg/` (SVG em mm, para extrudar
  no CAD — é o que a produção usa) e `qrcodes/` (PNG, só para conferência e tela)
- Os QRs são **limpos**: nada impresso dentro nem fora. 33 módulos, correção de
  erro M, borda de 2 módulos.
- **Quem identifica a plaquinha é a página**, não o QR: escaneando um código
  ainda não configurado, o `index.html` mostra o número em letra grande. Foi a
  escolha dele em 17/09/2026, melhor que o rótulo dentro do QR — que ficaria
  ilegível nos tamanhos pequenos que se cogitou antes.
- Tamanho na peça: **32 mm** de lado, impresso em 3D junto com a plaquinha.
  Ver "A plaquinha física" no fim deste arquivo para o porquê — não é o mesmo
  piso de um adesivo em papel (que seria 13 mm), porque em 3D o limite é a
  largura da linha de extrusão, não a tinta.

## NFC e QR: o mesmo código

A plaquinha carrega os dois leitores e os dois guardam a MESMA string:
`https://filard18.github.io/qr-avaliacoes/?c=NNN`.

O NFC nunca guarda o destino do cliente. Consequência: ativar uma plaquinha no
`redirects.json` atualiza QR e NFC ao mesmo tempo, sem tocar no chip. Não existe
"subir para o NFC" — não há nada a subir.

O único passo físico é gravar `?c=NNN` na tag, uma vez, na montagem, e depois
**proteger com senha**. Rastreado pelas colunas `NFC gravado` e `Montada` do
Notion (manuais: são estado físico, o sync não mexe nelas).

### Tag destravada aceita escrita de qualquer um

Uma tag NFC sem proteção é regravável por qualquer pessoa com um celular e o
NFC Tools, em segundos, sem senha nenhuma. Um concorrente pode apontar a
plaquinha do cliente para a página dele, e não fica nenhum sinal visível —
diferente de um adesivo colado sobre o QR, que se vê.

Correção de uma orientação anterior deste arquivo: até 17/09/2026 aqui estava
escrito "nunca bloquear a tag". Isso valia para o plano antigo, em que a tag
guardaria a URL do cliente e precisaria ser trocada. No desenho atual a tag
guarda `?c=NNN` e nunca muda, então deixá-la aberta não dá benefício algum.

**Proteger com senha, não travar como somente leitura.** A senha barra
estranho e mantém a tag corrigível; travar é irreversível e custa caro em dois
cenários concretos:

- Errar o número numa tag já embutida no plástico: sem correção possível, a
  plaquinha inteira vira refugo. Em 200 repetições, erro humano acontece.
- Migrar a URL (por exemplo apontar `owen.com.br` para o sistema, que
  encurtaria o QR): exigiria regravar todas as tags. Travadas, perde-se o lote.

Senha única para todo o lote, anotada fora daqui. Exige chip NTAG213/215/216 —
conferir antes de comprar, tag genérica pode não ter a função.

Ordem obrigatória na montagem: gravar, **conferir lendo de volta**, e só então
proteger. Nunca proteger antes de conferir.

### Tag sem gravar: Android avisa, iPhone fica mudo

Constatado em 23/09/2026 nas 10 primeiras plaquinhas. É normal, não é defeito:
o iPhone só reage a tag com NDEF válido (na prática, registro de URL) e ignora
tag vazia em silêncio; o Android avisa que está vazia.

Se ele relatar "iPhone não faz nada", a resposta depende do estado da tag:

- **Ainda não gravada** → esperado, nada a investigar. E o Android dizendo
  "vazia" já prova que o chip está vivo, que o sinal atravessa o plástico na
  espessura usada e que a tag está bem posicionada — os três riscos reais da
  montagem.
- **Já gravada e ainda mudo** → quase sempre o registro foi gravado como
  "Texto" em vez de "URL/URI". O Android mostra os dois; o iPhone só abre URL.
  Depois disso, conferir se o chip é NTAG213/215/216.

Ao testar no iPhone: a antena fica no topo das costas do aparelho, a tela
precisa estar ligada e desbloqueada, e câmera ou carteira abertas capturam o
NFC antes do sistema.

### "Erro durante o processo de escrita": a lista do NFC Tools acumula

Aconteceu em 23/09/2026, nas tags 003 e 009. **As tags estavam boas** — erro de
operação, não de hardware. É o primeiro lugar a olhar quando ele relatar falha
de gravação.

O "Adicionar um registro" do NFC Tools **acrescenta** à lista, não substitui.
Gravando uma plaquinha atrás da outra sem limpar, a lista acumula.

A conta: cada registro de URL `.../?c=NNN` ocupa **44 bytes**; a NTAG213 tem
**144**. Então a 4ª gravação seguida (176 bytes) estoura e dá erro — exatamente
o que aconteceu (004, 002, 005 gravaram; 003 e 009 falharam, com a tela
mostrando `Escrever / 220 Bytes` = 5 registros).

O estrago maior não é o erro, é o silêncio antes dele: **002 e 005 gravaram com
sucesso carregando também os registros anteriores.** Tag com vários registros
faz o celular abrir o **primeiro** — as duas mandavam o cliente para o destino
da 004. Grava, diz "concluído", e a plaquinha sai errada.

**Defesa permanente: o botão de gravar tem que dizer `44 Bytes`.** Qualquer
número maior (88, 132, 176...) significa lixo na lista. É a verificação mais
barata que existe aqui — um número só, antes de cada gravação.

Se ele pedir para "gravar o NFC do cliente X", a resposta é que já está feito
pelo cadastro no JSON — e nunca sugerir gravar a URL do cliente direto na tag,
que é o que quebraria o sistema desse lado.

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
5. Confirmar em 1 linha: código, cliente, e que QR **e** NFC já apontam para lá

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
- Para descer abaixo de 32 mm em 3D (ou de 13 mm em adesivo) seria preciso
  encurtar a URL: renomear o repo
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
| `URL destino`, `Configurado no GitHub` | GitHub (`redirects.json`) |
| `Cliente`, `Status`, `Valor`, `Data da venda`, `Telefone`, `Observações` | Notion |

`Cliente` saiu do GitHub em 17/09/2026: o `redirects.json` é público e expor a
lista de clientes entrega a carteira. O nome passou a ser escrito direto no
Notion por quem ativa a plaquinha. Para o usuário nada mudou — ele manda a
mesma mensagem e os dois lados são preenchidos.

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

## A plaquinha física (decidido em 17/09/2026)

Tudo impresso em 3D, nada de adesivo. Base branca, 95 x 150 mm, seis elementos
centralizados e empilhados, todos na mesma face e na mesma altura de camada —
uma única troca de filamento (M600) pinta os seis.

| Elemento | Medida | Topo (mm) |
| --- | --- | --- |
| "Avalie a gente" | letra 6,5 mm | 11 |
| Google | 26 mm | 27 |
| Símbolo NFC | 19 mm | 61 |
| "ou escaneie" | letra 4,5 mm | 86 |
| QR | 32 mm | 97 |
| www.owen.com.br | letra 5 mm | 136 |

Design: https://claude.ai/artifact/SpgybncKHcq55XL6dMkVLt

Arte do QR para a produção: `qrcodes_svg/NNN.svg`. Unidade do viewBox = 1 mm,
arquivo já em 32 x 32 mm, para importar 1:1 e extrudar. O retângulo vermelho
`limite-nao-extrudar` marca a borda externa: é referência de posicionamento,
não entra na extrusão.

### Limites que não se mexe

- **QR em 32 mm.** 37 módulos com a borda; em 32 mm cada módulo tem 0,86 mm =
  2 linhas de bico 0.4. Menos que isso os módulos se fundem na impressão. Foi o
  que forçou a plaquinha a crescer: em 70 x 90 mm o QR não cabia.
- **Texto com no mínimo 4,5 mm de altura**, gravado (sulco), não em relevo. A
  haste de uma fonte bold tem ~altura/7; abaixo de 4,5 mm ela fica mais fina que
  uma linha de extrusão e a letra sai quebrada. Uma versão anterior tinha texto
  de 3,2 mm, que não imprimiria.
- **Borda branca do QR: 1,7 mm** (2 módulos), sem textura nenhuma.
- **Cavidade da tag:** ø 27 mm centrada atrás do símbolo NFC, 1,2 mm de plástico
  por cima. Não colide com o QR (folga de 17 mm).

### Por que a frase "Avalie a gente" existe

Não é enfeite. O símbolo de aproximação é lido universalmente como "pague aqui",
então sem uma linha dizendo para que serve a plaquinha pode passar por
maquininha de cartão. A frase é neutra de propósito: o Google proíbe pedir nota
alta ("avalie com 5 estrelas" viola a política e pode punir o perfil do cliente).

### Cor do logo do Google

Quatro cores na mesma camada exigiriam AMS/MMU ou 4 trocas manuais. A prancha
"Uma troca de filamento" mostra a versão toda preta, que produz com um swap só.
O logo do Google é marca registrada — eles têm material oficial de avaliação com
regras de uso, não conferido ainda.

## O arquivo público não guarda nome de cliente

`redirects.json` é servido publicamente pelo GitHub Pages e o repositório é
público (tem que ser, senão o Pages não serve). Qualquer pessoa abre e lê.

Por isso ele guarda só `{"NNN": {"url": "..."}}`. O nome do cliente vive
exclusivamente no Notion. O validador trata o campo `cliente` como erro para
que ele não volte por descuido.

As URLs em si continuam visíveis, e isso é aceitável: são links públicos de
avaliação dos próprios clientes. O que não é aceitável é a lista de quem são.

Nenhum nome real chegou a ser commitado antes da mudança — o histórico está
limpo, só tem um "TESTE SYNC - ignorar" de um teste de sincronia.

## Como ele manda uma venda

Combinado em 23/09/2026. A mensagem vem assim, e nada mais:

```
007, Zilda Verdurão, ChIJxxxxxxxxxxxxx
```

Número da placa, nome do local, **Place ID puro**. Ele não monta a URL — você monta:

```
https://search.google.com/local/writereview?placeid=<PLACE_ID>
```

Motivo da escolha: no computador dele o Place ID sai em um passo (Place ID
Finder, ou a janelinha de "Escrever uma avaliação"), enquanto montar a URL à
mão é onde ele errava — mandava a URL da página de busca do Google, que cai
numa lista de resultados em vez do formulário de estrelas.

O que fazer com cada parte:

| Vem | Vai para |
|---|---|
| número | a chave no `redirects.json` |
| Place ID | vira a URL, e só a URL entra no `redirects.json` |
| nome do local | **só no Notion**, coluna `Cliente` — nunca no repo, que é público |

Se ele mandar uma URL pronta no lugar do Place ID (`g.page/r/.../review` ou
qualquer outra), use como veio. Só confira que começa com `https://`.

Um link de avaliação válido sempre tem `writereview` ou é um
`g.page/r/.../review`. Um `google.com/search?q=` ou `maps.app.goo.gl` **não
serve** — abre a página do negócio, não o formulário. Recuse e peça o Place ID.
