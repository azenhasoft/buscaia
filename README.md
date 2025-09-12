# Sistema de Busca em Documentos SharePoint

Sistema inteligente para buscar dados de funcionários em documentos do SharePoint, incluindo PDFs, ZIPs, DOCX e arquivos de texto.

## 🚀 Funcionalidades

- **Busca Inteligente**: Encontra dados por nome ou CPF (com ou sem formatação)
- **Suporte a Múltiplos Formatos**: PDF, ZIP, DOCX, TXT, CSV
- **Extração Automática**: Identifica automaticamente:
  - Nome do funcionário
  - CPF
  - RG  
  - Número do contrato (formato nnnnn/aaaa)
- **Busca Recursiva**: Varre todas as subpastas automaticamente
- **Interface Amigável**: Interface gráfica intuitiva com TKinter
- **Exportação**: Gera relatórios em CSV para análise

## 📋 Pré-requisitos

Antes de executar, instale as dependências:

```bash
pip install PyPDF2 pdfplumber python-docx pandas
```

## 🎯 Como Usar

### 1. Executar o Sistema
```bash
python busca_documentos.py
```

### 2. Configurar a Busca
1. **Selecionar Pasta**: Clique em "Selecionar" e escolha a pasta raiz do SharePoint
2. **Digitar Termo**: Informe o nome ou CPF do funcionário
3. **Iniciar Busca**: Clique em "Buscar"

### 3. Analisar Resultados
O sistema mostrará:
- ✅ Nome do funcionário encontrado
- ✅ CPF, RG e número do contrato
- 📁 Arquivo e caminho onde os dados foram encontrados
- 🔍 Trecho do texto onde a informação foi localizada

### 4. Exportar Resultados
Clique em "Exportar CSV" para gerar um relatório completo com todos os dados encontrados.

## 🏗️ Estrutura do Código

```
sistema-busca-documentos/
│
├── busca_documentos.py      # Código principal
├── README.md               # Este arquivo
└── requirements.txt        # Dependências do projeto
```

## 🔧 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **TKinter**: Interface gráfica
- **PyPDF2 & pdfplumber**: Leitura de PDFs
- **python-docx**: Leitura de documentos Word
- **pandas**: Exportação de dados para CSV

## 📊 Formatos Suportados

| Formato | Funcionalidade |
|---------|----------------|
| PDF | Extração completa de texto |
| ZIP | Busca dentro de arquivos compactados |
| DOCX | Leitura de documentos Word |
| TXT/CSV | Leitura de arquivos de texto |

## 🎨 Exemplo de Busca

### Busca por Nome:
```
Termo: "Maria Silva"
Resultado: Encontra todos os documentos que mencionam "Maria Silva"
```

### Busca por CPF:
```
Termo: "123.456.789-00" ou "12345678900"
Resultado: Encontra o CPF independente da formatação
```

## 📝 Padrões Reconhecidos

- **CPF**: `123.456.789-00` ou `12345678900`
- **RG**: `12.345.678-9` ou `123456789`
- **Contrato**: `12345/2023` (5 dígitos/4 dígitos)
- **Nomes**: Reconhece nomes completos e evita nomes de empresas

## ⚡ Performance

O sistema foi otimizado para:
- ✅ Processamento em segundo plano (não trava a interface)
- ✅ Leitura eficiente de grandes volumes de documentos
- ✅ Busca inteligente que evita falsos positivos
- ✅ Suporte a arquivos corrompidos (continua a busca)

## 🐛 Solução de Problemas

### Problema: Exportação CSV com colunas juntas
**Solução**: O código já inclui correção para exportação correta com delimitador `;`

### Problema: Encoding de caracteres especiais
**Solução**: Sistema usa UTF-8 com BOM para compatibilidade com Excel

### Problema: Arquivos ZIP com senha
**Solução**: No momento, o sistema não suporta arquivos ZIP protegidos por senha

## 📈 Próximas Melhorias

- [ ] Suporte a arquivos ZIP com senha
- [ ] Busca em imagens (OCR)
- [ ] Interface web adicional
- [ ] Relatórios em PDF
- [ ] Busca em lote (múltiplos funcionários)

## 👥 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commitar suas mudanças
4. Abrir um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Se encontrar problemas ou tiver sugestões:
1. Verifique se todas as dependências estão instaladas
2. Confirme que a pasta do SharePoint está acessível
3. Teste com arquivos de exemplo antes de usar em produção
---

**⭐ Se este projeto foi útil, deixe uma estrela no GitHub!**
