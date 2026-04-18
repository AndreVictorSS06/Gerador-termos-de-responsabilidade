from fpdf import FPDF
import webview
import os
import json
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Logo
        logo_path = os.path.join(os.getcwd(), 'gui', 'assets', 'logo.jpg')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        
        self.set_font('helvetica', 'B', 12)
        self.cell(40) # Space for logo
        self.cell(0, 10, 'Chamado - Gerador Automático (Grupo Serrana)', 0, 1, 'L')
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'{self.page_no()} / {{nb}}', 0, 0, 'R')

class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def generate_term(self, data):
        print("Recebido dados do formulário:", data)
        
        try:
            timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
            filename = f"Termo_{data['name'].replace(' ', '_')}.pdf"
            output_path = os.path.join(os.getcwd(), filename)
            
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.alias_nb_pages()
            pdf.add_page()
            
            # --- TABELA DE METADADOS (ESTILO GLPI) ---
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font('helvetica', 'B', 9)
            pdf.cell(0, 6, 'Empréstimo de Aparelho', 1, 1, 'C', fill=True)
            
            pdf.set_font('helvetica', 'B', 8)
            pdf.set_fill_color(255, 255, 255)
            
            # Linha 1
            pdf.cell(95, 6, f' Data de abertura: {timestamp}', 1, 0, 'L')
            pdf.cell(95, 6, f' Por: {data["name"]}', 1, 1, 'L')
            
            # Linha 2
            pdf.cell(95, 6, f' Última atualização: {timestamp} por {data["name"]}', 1, 1, 'L')
            
            # Linha 3
            pdf.cell(95, 6, f' Tempo para atendimento: {timestamp}', 1, 0, 'L')
            pdf.cell(95, 6, f' Tempo para solução: {timestamp}', 1, 1, 'L')
            
            # Linha 4
            pdf.cell(95, 6, f' Tempo interno para atendimento:', 1, 0, 'L')
            pdf.cell(95, 6, f' Tempo interno para solução:', 1, 1, 'L')
            
            # Linha 5
            pdf.cell(95, 6, f' Tipo: Requisição', 1, 0, 'L')
            pdf.cell(95, 6, f' Categoria: {data["category"]}', 1, 1, 'L')
            
            # Linha 6
            pdf.cell(95, 6, f' Status: Fechado - {timestamp}', 1, 0, 'L')
            pdf.cell(95, 6, f' Origem da requisição: Formcreator', 1, 1, 'L')
            
            # Linha 7
            pdf.cell(95, 6, f' Urgência: Muito Baixa', 1, 0, 'L')
            pdf.cell(95, 6, f' Aprovação: Não está sujeita a aprovação', 1, 1, 'L')
            
            # Linha 8
            pdf.cell(95, 6, f' Impacto: Muito Baixo', 1, 0, 'L')
            pdf.cell(95, 6, f' Localização: Grupo Serrana > Matriz', 1, 1, 'L')
            
            # Linha 9
            pdf.cell(95, 6, f' Prioridade: Muito Baixa', 1, 1, 'L')
            
            # Requerente e outros
            pdf.cell(190, 6, f' Requerente: {data["name"]}', 1, 1, 'L')
            pdf.cell(190, 6, f' Grupo requerente:', 1, 1, 'L')
            pdf.cell(190, 6, f' Observador:', 1, 1, 'L')
            pdf.cell(190, 6, f' Grupo observador: Atendimento > TI', 1, 1, 'L')
            pdf.cell(190, 6, f' Atribuído para técnicos:', 1, 1, 'L')
            pdf.cell(190, 6, f' Atribuído para grupos:', 1, 1, 'L')
            pdf.cell(190, 6, f' Atribuído a um fornecedor:', 1, 1, 'L')
            pdf.cell(190, 6, f' Título: Empréstimo de Aparelho', 1, 1, 'L')

            pdf.ln(5)
            
            # --- DADOS DO FORMULÁRIO ---
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, 'Dados do formulário', 0, 1, 'L')
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 8, 'Preencha os campos abaixo', 0, 1, 'L')
            
            pdf.set_font('helvetica', '', 9)
            fields = [
                (f"1) Selecione a Categoria :", data['category']),
                (f"2) Nome :", data['name']),
                (f"3) CPF :", data['cpf']),
                (f"4) Marca :", data['brand']),
                (f"5) Modelo :", data['model']),
                (f"6) IMEI :", data['imei']),
                (f"7) Data de Entrega :", data['delivery_date']),
                (f"8) Data de Devolução :", data['return_date'] or "Não informada"),
                (f"9) Valor :", data['value']),
                (f"10) Descrição :", data['description']),
            ]
            
            for label, value in fields:
                pdf.set_font('helvetica', 'B', 9)
                pdf.write(6, label + " ")
                pdf.set_font('helvetica', '', 9)
                pdf.write(6, value + "\n")
            
            # Page 2 - Clauses
            pdf.add_page()
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(45, 10, 'Termo de Responsabilidade', 1, 0, 'C', fill=True)
            pdf.cell(45, 10, timestamp, 1, 0, 'C')
            pdf.cell(45, 10, 'André Victor', 1, 0, 'C')
            pdf.cell(55, 10, 'Status: Feito', 1, 1, 'C')
            
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 7, 'Descrição:', 0, 1)
            
            clauses = [
                "1. Detenção e Uso Exclusivo:\nReconheço que possuo apenas a DETENÇÃO dos equipamentos, destinados exclusivamente à prestação de serviços profissionais, e NÃO a PROPRIEDADE dos mesmos.\nÉ terminantemente proibido emprestar, alugar ou ceder os equipamentos a terceiros.",
                "2. Comunicação de Danos, Inutilização ou Extravio:\nCaso ocorra dano, inutilização ou extravio dos equipamentos, comprometendo-me a informar imediatamente o setor competente.",
                "3. Devolução dos Equipamentos:\nAo término dos serviços ou em caso de rescisão do contrato de trabalho, devo devolver os equipamentos completos e em perfeito estado de conservação, considerando o desgaste natural pelo uso.",
                "4. Uso Restrito dos Equipamentos:\nÉ proibido utilizar os aparelhos para:\n- Envio de mensagens de texto pessoais.\n- Navegação na internet para fins não relacionados ao trabalho.\n- Realização de ligações que não sejam exclusivamente para a prestação de serviços da empresa.\n- Ligações para outros números devem ser feitas a cobrar. Caso contrário, o valor referente ao uso pessoal será cobrado com base na fatura do mês.",
                "5. Inspeções:\nEstou ciente de que os equipamentos em minha posse estarão sujeitos a inspeções sem prévio aviso.\n\nDeclaro estar ciente e de acordo com os termos acima."
            ]
            
            pdf.set_font('helvetica', '', 9)
            for clause in clauses:
                pdf.multi_cell(0, 5, clause)
                pdf.ln(3)

            # Signatures
            pdf.ln(10)
            pdf.line(20, pdf.get_y(), 90, pdf.get_y())
            pdf.line(110, pdf.get_y(), 180, pdf.get_y())
            pdf.set_font('helvetica', 'B', 8)
            pdf.cell(90, 5, 'Assinatura do Colaborador', 0, 0, 'C')
            pdf.cell(90, 5, 'Assinatura Responsável TI', 0, 1, 'C')

            pdf.output(output_path)
            
            # Open the PDF automatically after generation
            os.startfile(output_path)
            
            return {
                "success": True, 
                "message": f"Termo gerado: {filename}"
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False, 
                "error": str(e)
            }

def main():
    api = Api()
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')
    index_path = os.path.join(gui_dir, 'index.html')
    
    window = webview.create_window(
        'STRS - Gerador de Termos de Responsabilidade',
        index_path,
        js_api=api,
        width=950,
        height=850,
        resizable=True
    )
    
    api.set_window(window)
    webview.start(debug=True)

if __name__ == '__main__':
    main()
