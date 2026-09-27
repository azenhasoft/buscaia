# BuscaIA — Busca local em documentos

Aplicação desktop em Python para localizar informações em coleções de documentos armazenadas em uma pasta local ou sincronizada, como uma biblioteca do SharePoint sincronizada no computador.

O projeto nasceu de um problema prático: encontrar rapidamente referências a uma pessoa ou CPF em muitos arquivos, sem precisar abrir cada documento manualmente.

> **Importante:** o BuscaIA não se conecta diretamente à API do SharePoint. A aplicação trabalha com arquivos acessíveis pelo sistema de arquivos local.

## O que o projeto faz

- Pesquisa por **nome ou CPF**, inclusive CPF com ou sem formatação.
- Percorre a pasta escolhida e suas subpastas.
- Lê arquivos **PDF, DOCX, TXT e CSV**.
- Abre arquivos **ZIP** e pesquisa PDFs contidos neles.
- Procura padrões de **CPF, RG e número de contrato**.
- Mostra o arquivo, caminho relativo e um trecho de contexto do resultado.
- Executa a busca em uma thread separada para manter a interface responsiva.
- Exporta os resultados para **CSV** com codificação UTF-8 BOM e separador `;`.

## Tecnologias

- Python
- Tkinter / ttk
- pdfplumber
- python-docx
- pandas
- zipfile, tempfile, threading e expressões regulares da biblioteca padrão

## Como executar

Requer Python 3.8 ou superior.

```bash
git clone https://github.com/azenhasoft/buscaia.git
cd buscaia
pip install -r requirements.txt
python buscaia.py
```

A interface permite selecionar uma pasta, informar um nome ou CPF e iniciar a pesquisa. Os resultados encontrados aparecem em uma tabela e podem ser exportados para CSV.

## Formatos tratados

| Formato | Comportamento atual |
| --- | --- |
| PDF | Extração de texto com `pdfplumber` |
| DOCX | Leitura de parágrafos e tabelas |
| TXT / CSV | Leitura de texto com tentativa de diferentes encodings |
| ZIP | Pesquisa em PDFs armazenados dentro do arquivo compactado |

Arquivos `.doc` podem ser identificados pela aplicação, mas `python-docx` trabalha nativamente com DOCX; portanto, documentos no formato DOC antigo podem não ser processados corretamente.

## Como a busca funciona

A aplicação percorre recursivamente os arquivos da pasta selecionada. Quando encontra um formato tratado, extrai seu conteúdo textual e procura o termo informado.

Para CPF, a busca também compara sequências numéricas sem pontuação. Expressões regulares são usadas para localizar padrões de CPF, RG e contrato. A aplicação tenta associar um nome ao resultado por meio de padrões textuais e contexto próximo.

Essas heurísticas são úteis para busca documental, mas **não constituem validação oficial de identidade ou dos números encontrados** e podem produzir associações incorretas em documentos complexos.

## Estrutura atual

```text
buscaia/
├── buscaia.py
├── requirements.txt
└── README.md
```

O projeto ainda está concentrado em um único módulo Python. Uma futura refatoração poderá separar interface, extração de documentos e regras de busca.

## Privacidade

O BuscaIA pode ser usado para pesquisar dados pessoais presentes em documentos. Use somente arquivos aos quais você tenha autorização de acesso e trate os resultados de acordo com as políticas de segurança e privacidade aplicáveis ao seu ambiente.

O repositório não inclui documentos reais de funcionários nem dados pessoais para demonstração.

## Limitações conhecidas

- Não possui integração direta com SharePoint ou Microsoft Graph.
- Não executa OCR em PDFs compostos apenas por imagens.
- ZIPs protegidos por senha não são suportados.
- Dentro de ZIPs, a busca atual é voltada a arquivos PDF.
- A extração de nome, CPF, RG e contrato é baseada em heurísticas e expressões regulares.
- Não há suíte automatizada de testes no estado atual do projeto.

## Próximos passos

- [ ] Separar interface, extração e regras de busca em módulos.
- [ ] Criar testes automatizados para normalização, busca e extração.
- [ ] Adicionar dados sintéticos de demonstração.
- [ ] Adicionar screenshot ou GIF da aplicação usando apenas dados fictícios.
- [ ] Avaliar suporte a OCR para documentos digitalizados.
- [ ] Melhorar a associação de dados ao trecho em que o termo foi encontrado.
- [ ] Avaliar busca em lote.

## Por que mantenho este projeto

Este repositório faz parte do meu processo de desenvolvimento em Python e automação. Ele representa uma aplicação funcional construída em torno de um problema documental concreto, mas também registra decisões e limitações que ainda pretendo melhorar.

Contribuições e sugestões são bem-vindas.
