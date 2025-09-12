import os
import re
import zipfile
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import PyPDF2
import pdfplumber
import docx
import pandas as pd
from pathlib import Path
import csv

class DocumentSearchApp:
    def __init__(self, root):
        # Configuração inicial da janela principal
        self.root = root
        self.root.title("Busca de Documentos - SharePoint")
        self.root.geometry("1200x800")
        
        # Setup da interface e variáveis
        self.setup_ui()
        self.search_results = []  # Onde vou guardar os resultados da busca
        
    def setup_ui(self):
        """Aqui eu crio toda a interface gráfica do programa"""
        # Frame principal onde tudo vai ficar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuro para a interface expandir quando a janela for redimensionada
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Campo para selecionar a pasta do SharePoint
        ttk.Label(main_frame, text="Pasta do SharePoint:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_path = tk.StringVar()  # Variável que guarda o caminho da pasta
        ttk.Entry(main_frame, textvariable=self.folder_path, width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Selecionar", command=self.select_folder).grid(row=0, column=2, padx=5)
        
        # Campo para digitar o que buscar (nome ou CPF)
        ttk.Label(main_frame, text="Buscar por (Nome ou CPF):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_term = tk.StringVar()  # Variável que guarda o termo de busca
        ttk.Entry(main_frame, textvariable=self.search_term, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Buscar", command=self.start_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar CSV", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Barra de progresso para mostrar que está trabalhando
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Área de resultados
        ttk.Label(main_frame, text="Resultados:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Tabela para mostrar os resultados encontrados
        columns = ('Nome', 'CPF', 'RG', 'Contrato', 'Arquivo', 'Caminho', 'Trecho Encontrado')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configuro o tamanho de cada coluna
        column_widths = {'Nome': 150, 'CPF': 120, 'RG': 100, 'Contrato': 100, 
                        'Arquivo': 150, 'Caminho': 200, 'Trecho Encontrado': 250}
        
        for col in columns:
            self.tree.heading(col, text=col)  # Nome da coluna
            self.tree.column(col, width=column_widths.get(col, 120))  # Largura da coluna
        
        self.tree.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Barra de rolagem para a tabela
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Status bar para mostrar mensagens
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    def select_folder(self):
        """Abre uma janela para o usuário selecionar a pasta do SharePoint"""
        folder = filedialog.askdirectory(title="Selecionar pasta do SharePoint")
        if folder:
            self.folder_path.set(folder)  # Guarda o caminho selecionado
    
    def start_search(self):
        """Inicia a busca quando o usuário clica no botão Buscar"""
        search_term = self.search_term.get().strip()  # Pega o que foi digitado
        folder_path = self.folder_path.get()  # Pega a pasta selecionada
        
        # Verificações básicas
        if not search_term:
            messagebox.showwarning("Aviso", "Digite um termo para buscar (nome ou CPF)")
            return
        
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showwarning("Aviso", "Selecione uma pasta válida")
            return
        
        # Executa a busca em uma thread separada para não travar a interface
        Thread(target=self.perform_search, args=(folder_path, search_term), daemon=True).start()
        self.progress.start()  # Animação da barra de progresso
        self.status_var.set("Buscando...")
    
    def perform_search(self, folder_path, search_term):
        """Função principal que faz a busca em todos os arquivos"""
        try:
            self.search_results = []  # Limpa resultados anteriores
            processed_files = 0  # Contador de arquivos processados
            
            # Padrões que uso para encontrar CPF, RG e contrato
            cpf_pattern = r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b'  # CPF com ou sem pontuação
            rg_pattern = r'\b\d{2}\.\d{3}\.\d{3}-\d{1}\b|\b\d{7,9}\b'  # RG com ou sem pontuação
            contrato_pattern = r'\b\d{5}/\d{4}\b'  # Contrato no formato nnnnn/aaaa
            
            # Percorro TODAS as pastas e subpastas
            for root_dir, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    relative_path = os.path.relpath(file_path, folder_path)  # Caminho relativo
                    
                    try:
                        file_lower = file.lower()  # Nome do arquivo em minúsculo
                        
                        # Verifico o tipo de arquivo pela extensão
                        if file_lower.endswith('.pdf'):
                            # Busco em arquivos PDF
                            results = self.search_pdf(file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern)
                            for result in results:
                                result['Arquivo'] = file
                                result['Caminho'] = relative_path
                                self.search_results.append(result)
                        
                        elif file_lower.endswith('.zip'):
                            # Busco dentro de arquivos ZIP
                            results = self.search_zip(file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern)
                            for result in results:
                                result['Arquivo'] = f"{file} -> {result['Arquivo']}"
                                result['Caminho'] = relative_path
                                self.search_results.append(result)
                        
                        elif file_lower.endswith(('.doc', '.docx')):
                            # Busco em documentos Word
                            results = self.search_docx(file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern)
                            for result in results:
                                result['Arquivo'] = file
                                result['Caminho'] = relative_path
                                self.search_results.append(result)
                        
                        elif file_lower.endswith(('.txt', '.csv')):
                            # Busco em arquivos de texto
                            results = self.search_text_file(file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern)
                            for result in results:
                                result['Arquivo'] = file
                                result['Caminho'] = relative_path
                                self.search_results.append(result)
                        
                        processed_files += 1  # Mais um arquivo processado
                        
                        # Atualizo o status a cada 10 arquivos
                        if processed_files % 10 == 0:
                            self.root.after(0, lambda: self.status_var.set(
                                f"Processados {processed_files} arquivos... {len(self.search_results)} encontrado(s)"
                            ))
                        
                    except Exception as e:
                        # Se der erro em algum arquivo, continuo com os próximos
                        print(f"Erro ao processar {file_path}: {e}")
            
            # Atualizo a interface com os resultados
            self.root.after(0, self.update_results)
            
        except Exception as e:
            # Se der erro geral, mostro mensagem
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante a busca: {str(e)}"))
        finally:
            # Sempre executo isso, mesmo se der erro
            self.root.after(0, self.search_completed)
    
    def search_pdf(self, file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern):
        """Busca em arquivos PDF"""
        results = []
        try:
            text = ""
            # Uso o pdfplumber que é melhor para extrair texto
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"  # Junto texto de todas as páginas
            
            # Verifico se o termo de busca está neste texto
            if self.contains_search_term(text, search_term):
                # Encontro o contexto onde o termo foi achado
                context = self.find_search_context(text, search_term)
                # Extraio os dados do funcionário
                result = self.extract_employee_data(text, search_term, cpf_pattern, rg_pattern, contrato_pattern, context)
                result['Trecho Encontrado'] = context[:200] + "..." if len(context) > 200 else context
                results.append(result)
        
        except Exception as e:
            print(f"Erro ao ler PDF {file_path}: {e}")
        
        return results
    
    def search_zip(self, file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern):
        """Busca dentro de arquivos ZIP"""
        results = []
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Pulo pastas e arquivos do sistema
                    if not file_info.is_dir() and not file_info.filename.startswith('__MACOSX'):
                        # Só procuro em PDFs dentro do ZIP
                        if file_info.filename.lower().endswith('.pdf'):
                            with zip_ref.open(file_info.filename) as file:
                                content = file.read()  # Leio o conteúdo
                            
                            # Crio um arquivo temporário para processar o PDF
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                                temp_file.write(content)
                                temp_file_path = temp_file.name
                            
                            try:
                                # Busco no PDF temporário
                                zip_results = self.search_pdf(temp_file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern)
                                for result in zip_results:
                                    result['Arquivo'] = file_info.filename
                                    results.append(result)
                            finally:
                                # Sempre apago o arquivo temporário
                                os.unlink(temp_file_path)
        
        except Exception as e:
            print(f"Erro ao processar ZIP {file_path}: {e}")
        
        return results
    
    def search_docx(self, file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern):
        """Busca em documentos Word"""
        results = []
        try:
            doc = docx.Document(file_path)
            # Extraio texto dos parágrafos
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            # Também extraio texto das tabelas
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + "\n"
            
            if self.contains_search_term(text, search_term):
                context = self.find_search_context(text, search_term)
                result = self.extract_employee_data(text, search_term, cpf_pattern, rg_pattern, contrato_pattern, context)
                result['Trecho Encontrado'] = context[:200] + "..." if len(context) > 200 else context
                results.append(result)
        
        except Exception as e:
            print(f"Erro ao ler DOCX {file_path}: {e}")
        
        return results
    
    def search_text_file(self, file_path, search_term, cpf_pattern, rg_pattern, contrato_pattern):
        """Busca em arquivos de texto simples"""
        results = []
        try:
            # Tento diferentes codificações porque arquivos podem ter encoding diferente
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        text = f.read()  # Leio o arquivo
                    
                    if self.contains_search_term(text, search_term):
                        context = self.find_search_context(text, search_term)
                        result = self.extract_employee_data(text, search_term, cpf_pattern, rg_pattern, contrato_pattern, context)
                        result['Trecho Encontrado'] = context[:200] + "..." if len(context) > 200 else context
                        results.append(result)
                    break  # Se consegui ler, paro de tentar outras codificações
                except UnicodeDecodeError:
                    continue  # Se não conseguiu, tenta próxima codificação
        
        except Exception as e:
            print(f"Erro ao ler arquivo de texto {file_path}: {e}")
        
        return results
    
    def contains_search_term(self, text, search_term):
        """Verifica se o termo de busca está no texto"""
        # Limpo números para buscar CPF mesmo com formatação diferente
        search_term_clean = re.sub(r'\D', '', search_term)  # Tiro tudo que não é número
        text_clean = re.sub(r'\D', '', text)  # Faço o mesmo com o texto
        
        # Retorno True se encontrar o nome ou o CPF
        return (search_term.lower() in text.lower() or 
                search_term_clean in text_clean)
    
    def find_search_context(self, text, search_term, context_chars=100):
        """Encontra o trecho onde o termo foi achado"""
        # Se estou buscando por CPF
        if re.match(r'\d', search_term):
            search_term_clean = re.sub(r'\D', '', search_term)
            text_clean = re.sub(r'\D', '', text)
            if search_term_clean in text_clean:
                # Acho onde está o CPF no texto limpo
                pos = text_clean.find(search_term_clean)
                if pos != -1:
                    # Pego um pedaço do texto ao redor
                    start = max(0, pos - context_chars)
                    end = min(len(text), pos + len(search_term_clean) + context_chars)
                    return text[start:end]
        
        # Se estou buscando por nome
        if search_term.lower() in text.lower():
            pos = text.lower().find(search_term.lower())
            if pos != -1:
                start = max(0, pos - context_chars)
                end = min(len(text), pos + len(search_term) + context_chars)
                return text[start:end]
        
        return "Contexto não encontrado"
    
    def extract_employee_data(self, text, search_term, cpf_pattern, rg_pattern, contrato_pattern, context):
        """Extrai os dados do funcionário de forma inteligente"""
        result = {
            'Nome': '',
            'CPF': '',
            'RG': '',
            'Contrato': '',
            'Trecho Encontrado': ''
        }
        
        # Se estou buscando por CPF, tento achar o CPF correto
        if re.match(r'\d', search_term):
            cpf_encontrado = self.find_cpf_near_search(text, search_term, cpf_pattern)
            result['CPF'] = cpf_encontrado if cpf_encontrado else self.extract_first_match(text, cpf_pattern)
        else:
            # Se busco por nome, pego o primeiro CPF que achar
            result['CPF'] = self.extract_first_match(text, cpf_pattern)
        
        # RG e Contrato - pego a primeira ocorrência
        result['RG'] = self.extract_first_match(text, rg_pattern)
        result['Contrato'] = self.extract_first_match(text, contrato_pattern)
        
        # Nome - aqui uso um algoritmo mais esperto
        result['Nome'] = self.find_employee_name(text, search_term, result['CPF'], context)
        
        return result
    
    def find_cpf_near_search(self, text, search_term, cpf_pattern):
        """Tenta achar o CPF certo perto de onde foi feita a busca"""
        # Se já é um CPF formatado, retorno ele mesmo
        if re.match(cpf_pattern, search_term):
            return search_term
        
        # Se é CPF sem formatação, formato ele
        search_digits = re.sub(r'\D', '', search_term)
        if len(search_digits) == 11:
            return f"{search_digits[:3]}.{search_digits[3:6]}.{search_digits[6:9]}-{search_digits[9:]}"
        
        # Procuro CPFs que estejam perto de palavras como "funcionário"
        cpfs = re.finditer(cpf_pattern, text)
        for match in cpfs:
            cpf_pos = match.start()
            # Vejo o contexto ao redor do CPF
            context_start = max(0, cpf_pos - 200)
            context_end = min(len(text), cpf_pos + 200)
            context = text[context_start:context_end]
            
            # Se tem palavras de funcionário por perto, é provavelmente o CPF certo
            if any(word in context.lower() for word in ['funcionário', 'empregado', 'colaborador', 'nome', 'cpf']):
                return match.group()
        
        # Se não achei, pego o primeiro CPF do texto
        return self.extract_first_match(text, cpf_pattern)
    
    def find_employee_name(self, text, search_term, cpf, context):
        """Encontra o nome do funcionário de forma inteligente"""
        # Se estou buscando por nome, uso o próprio termo
        if not re.match(r'\d', search_term) and len(search_term.split()) >= 2:
            return search_term.title()  # Coloco a primeira letra maiúscula
        
        # Padrões para tentar achar o nome
        name_patterns = [
            r'(?i)(?:nome|funcionário|empregado)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?i)sr[\.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?i)sra[\.\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b(?=\s*(?:cpf|rg|contrato|funcionário))'
        ]
        
        # Testo cada padrão
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Prefiro nomes que tenham pelo menos nome e sobrenome
                for match in matches:
                    if len(match.split()) >= 2:
                        return match
        
        # Última tentativa: procuro sequências de palavras com iniciais maiúsculas
        nome_candidates = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
        for nome in nome_candidates:
            # Filtro nomes que parecem ser de empresas
            if (len(nome.split()) >= 2 and 
                not any(word in nome.lower() for word in ['ltda', 's/a', 'me', 'eireli', 'empresa', 'contratante'])):
                return nome
        
        return "Nome não identificado"
    
    def extract_first_match(self, text, pattern):
        """Pega a primeira ocorrência de um padrão no texto"""
        matches = re.findall(pattern, text)
        return matches[0] if matches else ''  # Retorno a primeira ou string vazia
    
    def update_results(self):
        """Atualiza a tabela com os resultados encontrados"""
        # Limpo a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adiciono cada resultado na tabela
        for result in self.search_results:
            self.tree.insert('', 'end', values=(
                result.get('Nome', ''),
                result.get('CPF', ''),
                result.get('RG', ''),
                result.get('Contrato', ''),
                result.get('Arquivo', ''),
                result.get('Caminho', ''),
                result.get('Trecho Encontrado', '')
            ))
    
    def search_completed(self):
        """Chamado quando a busca termina"""
        self.progress.stop()  # Paro a animação da barra
        self.status_var.set(f"Busca concluída. {len(self.search_results)} resultado(s) encontrado(s).")
    
    def clear_results(self):
        """Limpa todos os resultados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.search_results = []
        self.status_var.set("Resultados limpos")
    
    def export_results(self):
        """Exporta os resultados para CSV - CORRIGIDO"""
        if not self.search_results:
            messagebox.showinfo("Info", "Nenhum resultado para exportar")
            return
        
        # Peço para o usuário escolher onde salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Método 1: Usando csv.DictWriter (mais confiável)
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    # Defino as colunas que quero exportar
                    fieldnames = ['Nome', 'CPF', 'RG', 'Contrato', 'Arquivo', 'Caminho', 'Trecho Encontrado']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                    
                    # Escrevo o cabeçalho
                    writer.writeheader()
                    
                    # Escrevo cada linha de resultado
                    for result in self.search_results:
                        # Garanto que todas as colunas existem no resultado
                        row = {field: result.get(field, '') for field in fieldnames}
                        writer.writerow(row)
                
                messagebox.showinfo("Sucesso", f"Resultados exportados para {file_path}")
                
            except Exception as e:
                # Se der erro, tento método alternativo
                try:
                    self.alternative_export(file_path)
                    messagebox.showinfo("Sucesso", f"Resultados exportados para {file_path} (método alternativo)")
                except Exception as e2:
                    messagebox.showerror("Erro", f"Erro ao exportar: {str(e2)}")
    
    def alternative_export(self, file_path):
        """Método alternativo para exportação caso o primeiro falhe"""
        # Método 2: Usando pandas mas garantindo a formatação correta
        # Primeiro preparo os dados para garantir que estão no formato correto
        export_data = []
        for result in self.search_results:
            export_data.append({
                'Nome': result.get('Nome', ''),
                'CPF': result.get('CPF', ''),
                'RG': result.get('RG', ''),
                'Contrato': result.get('Contrato', ''),
                'Arquivo': result.get('Arquivo', ''),
                'Caminho': result.get('Caminho', ''),
                'Trecho Encontrado': result.get('Trecho Encontrado', '')
            })
        
        # Crio o DataFrame e exporto com configurações específicas
        df = pd.DataFrame(export_data)
        df.to_csv(file_path, sep=';', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)

def main():
    """Função principal que inicia o programa"""
    root = tk.Tk()  # Crio a janela principal
    app = DocumentSearchApp(root)  # Crio a aplicação
    root.mainloop()  # Inicio o loop principal da interface

if __name__ == "__main__":
    main()  # Executo o programa