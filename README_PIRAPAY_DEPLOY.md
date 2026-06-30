# PIRApay - Publicacao no GitHub Pages

Agora o relatorio executivo funciona com JavaScript no proprio navegador. Nao precisa rodar servidor Python para gerar o PDF.

## Como publicar

Suba para o GitHub pelo menos estes arquivos:

- `index.html`
- `PIRApayR.html`
- `assets/pirapay-logo.png`
- `pirapay-config.js`

Depois ative o GitHub Pages:

1. Va em **Settings** do repositorio.
2. Abra **Pages**.
3. Em **Build and deployment**, escolha **Deploy from a branch**.
4. Selecione a branch principal e a pasta raiz.
5. Abra a URL publicada pelo GitHub Pages.

## Como gerar o PDF executivo

1. Abra o sistema.
2. Altere as premissas da simulacao.
3. Clique em **Gerar PDF Executivo**.
4. O navegador abre a tela de impressao.
5. Escolha **Salvar como PDF**.

O relatorio usa os dados atuais da tela no momento do clique.

## Arquivos opcionais

Os arquivos abaixo ficaram no projeto caso voce queira voltar a usar geracao server-side no futuro, mas nao sao obrigatorios para GitHub Pages:

- `pirapay_pdf_server.py`
- `tmp/pdfs/generate_pirapay_pdf.py`
- `requirements.txt`
- `Procfile`
- `render.yaml`
- `runtime.txt`

