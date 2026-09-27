# BuscaIA

O BuscaIA nasceu de um problema bem simples: eu precisava encontrar informações espalhadas por muitos documentos sem abrir um por um.

A ideia foi criar uma aplicação desktop em Python que percorresse uma pasta, inclusive suas subpastas, e procurasse por nome ou CPF dentro dos arquivos.

No meu caso, essa pasta pode ser uma biblioteca do SharePoint sincronizada no computador. O programa não se conecta diretamente ao SharePoint nem usa Microsoft Graph. Para o BuscaIA, são arquivos locais como quaisquer outros.

## O que ele faz

Hoje o programa consegue:

- pesquisar por nome ou CPF;
- encontrar CPF mesmo quando a pontuação usada na busca é diferente da encontrada no documento;
- ler PDF, DOCX, TXT e CSV;
- procurar em PDFs que estejam dentro de arquivos ZIP;
- identificar padrões de CPF, RG e número de contrato;
- mostrar o arquivo, o caminho e um trecho onde a informação foi encontrada;
- exportar os resultados para CSV.

A interface foi feita com Tkinter. A busca roda em uma thread separada para não deixar a janela travada enquanto os documentos são processados.

## Como executar

O projeto requer Python 3.8 ou superior.

```bash
git clone https://github.com/azenhasoft/buscaia.git
cd buscaia
pip install -r requirements.txt
python buscaia.py
```

Depois de abrir o programa, basta escolher a pasta, informar um nome ou CPF e iniciar a busca.

## Tecnologias usadas

- Python
- Tkinter / ttk
- pdfplumber
- python-docx
- pandas
- expressões regulares
- zipfile e tempfile

## Formatos

| Formato | Como é tratado |
| --- | --- |
| PDF | Texto extraído com `pdfplumber` |
| DOCX | Leitura de parágrafos e tabelas |
| TXT / CSV | Leitura de texto com tentativa de diferentes encodings |
| ZIP | Pesquisa nos PDFs armazenados dentro do arquivo |

Existe uma verificação para arquivos `.doc` no código, mas a biblioteca `python-docx` trabalha com DOCX. Por isso, documentos antigos no formato DOC podem não funcionar corretamente.

## Como a busca funciona

O programa percorre os arquivos da pasta selecionada e extrai o texto dos formatos que consegue ler.

Quando a busca é por CPF, retiro os caracteres que não são números antes da comparação. Assim, uma busca por CPF sem pontuação também pode encontrar a versão formatada no documento.

Depois de encontrar o termo, o programa tenta localizar CPF, RG, contrato e nome usando expressões regulares e o texto próximo ao resultado.

Essa parte ainda é baseada em regras e heurísticas. Ela ajuda a localizar informações, mas não valida se um CPF, RG ou nome realmente pertence àquela pessoa. Em documentos mais complicados, a associação pode sair errada.

## Estrutura atual

```text
buscaia/
├── buscaia.py
├── requirements.txt
└── README.md
```

Por enquanto, praticamente toda a aplicação está em `buscaia.py`.

Funciona, mas não é a estrutura que quero manter conforme o projeto crescer. Um dos próximos passos é separar a interface, a leitura dos documentos e as regras de busca.

## O que ainda falta

Há algumas limitações que quero resolver aos poucos:

- PDFs que são apenas imagens não passam por OCR;
- ZIPs com senha não são suportados;
- dentro dos ZIPs, a busca atual procura apenas PDFs;
- a extração dos dados ainda depende de expressões regulares e heurísticas;
- ainda não escrevi testes automatizados;
- não existe integração direta com SharePoint ou Microsoft Graph.

Também quero criar arquivos fictícios para demonstração e colocar uma imagem ou GIF da aplicação funcionando. Assim posso mostrar o projeto sem usar documentos ou dados reais.

## Privacidade

Este programa pode ser usado em documentos que contenham dados pessoais.

Não coloquei documentos reais de funcionários no repositório e não pretendo fazer isso. Quem usar o BuscaIA deve trabalhar apenas com arquivos aos quais tenha autorização de acesso e seguir as regras de segurança e privacidade do próprio ambiente.

## Próximos passos

- [ ] Separar o código em módulos
- [ ] Criar testes automatizados
- [ ] Preparar documentos fictícios para demonstração
- [ ] Adicionar screenshot ou GIF da aplicação
- [ ] Experimentar OCR em documentos digitalizados
- [ ] Melhorar a associação entre os dados encontrados
- [ ] Testar uma busca em lote

## Por que este projeto está aqui

O BuscaIA não começou como exercício de curso. Ele nasceu de um problema que eu queria resolver.

Ainda tem coisas que eu faria diferente e outras que nem implementei. É justamente por isso que quero continuar trabalhando nele.

Para mim, este repositório serve tanto para mostrar o que já consegui construir quanto para registrar o que ainda estou aprendendo.
