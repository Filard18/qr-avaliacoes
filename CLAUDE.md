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
- QR codes gerados: `001` a `150`, em `qrcodes/` (PNG) e `folha_plaquinhas_001-150.pdf`
- O número fica **pequeno e discreto dentro do próprio QR**, canto inferior direito
  (5x3 módulos, preto, correção de erro H). O cliente não deve ver número na
  plaquinha — ele existe só para o vendedor identificar qual código é qual.
  Nunca gerar QR com o número grande embaixo para a arte da plaquinha.

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
