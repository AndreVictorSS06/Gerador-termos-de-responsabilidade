from fpdf import FPDF
import os
from datetime import datetime

class PDFTerm(FPDF):
    def header(self):
        logo_path = os.path.join(os.getcwd(), 'gui', 'assets', 'logo.jpg')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        self.set_font('helvetica', 'B', 12)
        self.cell(40)
        self.cell(0, 10, 'Chamado - Gerador Automático (Grupo Serrana)', 0, 1, 'L')
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'{self.page_no()} / {{nb}}', 0, 0, 'R')

class PDFService:
    @staticmethod
    def generate(data, output_path):
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
        
        pdf = PDFTerm()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # --- TABELA DE CABEÇALHO (REPLICA EXATA GLPI) ---
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(0, 6, 'Empréstimo de Aparelho', 1, 1, 'C', fill=True)
        
        pdf.set_font('helvetica', 'B', 8)
        pdf.set_fill_color(255, 255, 255)
        
        # Grid de metadados
        pdf.cell(95, 6, f' Data de abertura: {timestamp}', 1, 0, 'L')
        pdf.cell(95, 6, f' Por: {data["technician"]}', 1, 1, 'L')
        pdf.cell(190, 6, f' Última atualização: {timestamp} por {data["technician"]}', 1, 1, 'L')
        pdf.cell(95, 6, f' Tempo para atendimento: {timestamp}', 1, 0, 'L')
        pdf.cell(95, 6, f' Tempo para solução: {timestamp} SLA: 48h (TI)', 1, 1, 'L')
        pdf.cell(95, 6, f' Tempo interno para atendimento:', 1, 0, 'L')
        pdf.cell(95, 6, f' Tempo interno para solução:', 1, 1, 'L')
        pdf.cell(95, 6, f' Tipo: Requisição', 1, 0, 'L')
        pdf.cell(95, 6, f' Categoria: {data["category"]}', 1, 1, 'L')
        pdf.cell(95, 6, f' Status: Fechado - {timestamp}', 1, 0, 'L')
        pdf.cell(95, 6, f' Origem da requisição: Formcreator', 1, 1, 'L')
        pdf.cell(95, 6, f' Urgência: Muito Baixa', 1, 0, 'L')
        pdf.cell(95, 6, f' Aprovação: Não está sujeita a aprovação', 1, 1, 'L')
        pdf.cell(95, 6, f' Impacto: Muito Baixo', 1, 0, 'L')
        pdf.cell(95, 6, f' Localização: Grupo Serrana > Piauí > Serrana', 1, 1, 'L')
        pdf.cell(95, 6, f' Prioridade: Muito Baixa', 1, 1, 'L')
        
        # Linhas de Requerente/Grupo
        pdf.cell(190, 6, f' Requerente: {data["technician"]}', 1, 1, 'L')
        pdf.cell(190, 6, f' Grupo requerente:', 1, 1, 'L')
        pdf.cell(190, 6, f' Observador:', 1, 1, 'L')
        pdf.cell(190, 6, f' Grupo observador: Atendimento > TI', 1, 1, 'L')
        pdf.cell(190, 6, f' Atribuído para técnicos:', 1, 1, 'L')
        pdf.cell(190, 6, f' Atribuído para grupos:', 1, 1, 'L')
        pdf.cell(190, 6, f' Atribuído a um fornecedor:', 1, 1, 'L')
        pdf.cell(190, 6, f' Título: Empréstimo de Aparelho', 1, 1, 'L')
        pdf.cell(190, 6, f' Descrição:', 1, 1, 'L')
        pdf.ln(5)

        # --- CONTEÚDO DO FORMULÁRIO ---
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'Dados do formulário', 0, 1, 'L')
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, 'Preencha os campos abaixo', 0, 1, 'L')
        
        pdf.set_font('helvetica', '', 9)
        
        def add_field(num, label, value):
            pdf.set_font('helvetica', 'B', 9)
            pdf.write(6, f"{num}) {label} : ")
            pdf.set_font('helvetica', '', 9)
            pdf.write(6, f"{value}\n")

        add_field(1, "Selecione a Categoria", data["category"])
        add_field(2, "Nome", data["name"].upper())
        add_field(3, "CPF", data["cpf"])
        add_field(4, "Marca", data["brand"])
        add_field(5, "Modelo", data["model"])
        add_field(6, "IMEI", data["imei"])
        add_field(7, "Data de Entrega", data["delivery_date"])
        add_field(8, "Data de Devolução", data["return_date"] or "")
        add_field(9, "Valor", data["value"])
        
        pdf.set_font('helvetica', 'B', 9)
        pdf.write(6, "10) Descrição : \n\n")
        pdf.set_font('helvetica', '', 9)
        pdf.multi_cell(0, 5, data["description"])
        
        pdf.ln(5)

        # --- ACOMPANHAMENTOS E TAREFAS ---
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(0, 6, 'Acompanhamentos: Nenhum item para ser mostrado', 1, 1, 'C', fill=True)
        pdf.ln(2)
        pdf.cell(0, 6, 'Tarefa de chamado: 1', 1, 1, 'C', fill=True)
        pdf.set_font('helvetica', 'I', 8)
        cols = [("Tipo", 34), ("Data", 39), ("Duração", 39), ("Autor", 39), ("Planejamento", 39)]
        for label, width in cols:
            pdf.cell(width, 6, label, 1, 0, 'C', fill=True)
        pdf.ln(10)

        # --- PÁGINA 2: MANTER IGUAL ---
        pdf.add_page()
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font('helvetica', 'B', 8)
        pdf.cell(35, 6, ' Termo de Responsabilidade', 1, 0, 'L', fill=True)
        pdf.cell(35, 6, f' {timestamp}', 1, 0, 'C', fill=True)
        pdf.cell(35, 6, ' 0 segundo', 1, 0, 'C', fill=True)
        pdf.cell(50, 6, f' {data["name"]}', 1, 0, 'C', fill=True)
        pdf.cell(35, 6, ' Status: Feito', 1, 1, 'C', fill=True)
        pdf.set_font('helvetica', 'B', 9); pdf.cell(0, 6, 'Descrição:', 0, 1, 'L')
        pdf.set_font('helvetica', '', 9)
        clausulas = [
            "1. Detenção e Uso Exclusivo:\nReconheço que possuo apenas a DETENÇÃO dos equipamentos, destinados exclusivamente à prestação de serviços profissionais, e NÃO a PROPRIEDADE dos mesmos. É terminantemente proibido emprestar, alugar ou ceder os equipamentos a terceiros.",
            "2. Comunicação de Danos, Inutilização ou Extravio:\nCaso ocorra dano, inutilização ou extravio dos equipamentos, comprometendo-me a informar imediatamente o setor competente.",
            "3. Devolução dos Equipamentos:\nAo término dos serviços ou em caso de rescisão do contrato de trabalho, devo devolver os equipamentos completos e em perfeito estado de conservação, considerando o desgaste natural pelo uso.",
            "4. Uso Restrito dos Equipamentos:\nÉ proibido utilizar os aparelhos para:\n- Envio de mensagens de texto pessoais.\n- Navegação na internet para fins não relacionados ao trabalho.\n- Realização de ligações que não sejam exclusivamente para a prestação de serviços da empresa.\n- Ligações para outros números devem ser feitas a cobrar. Caso contrário, o valor referente ao uso pessoal será cobrado com base na fatura do mês.",
            "5. Inspeções:\nEstou ciente de que os equipamentos em minha posse estarão sujeitos a inspeções sem prévio aviso."
        ]
        for item in clausulas:
            pdf.multi_cell(0, 5, item); pdf.ln(2)
        pdf.set_font('helvetica', 'B', 9); pdf.cell(0, 10, 'Declaro estar ciente e de acordo com os termos acima.', 0, 1, 'L')
        pdf.ln(5); pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 6, 'Documento: Nenhum item para ser mostrado', 1, 1, 'C', fill=True)
        pdf.ln(2); pdf.cell(0, 6, 'Solução: Nenhum item para ser mostrado', 1, 1, 'C', fill=True)
        pdf.ln(15); pdf.line(20, pdf.get_y(), 90, pdf.get_y()); pdf.line(110, pdf.get_y(), 180, pdf.get_y())
        pdf.set_font('helvetica', 'B', 8); pdf.cell(90, 5, 'Assinatura do Colaborador', 0, 0, 'C'); pdf.cell(90, 5, 'Assinatura Responsável TI', 0, 1, 'C')

        pdf.output(output_path)
        return output_path
