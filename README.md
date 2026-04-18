# STRS - Sistema de Termos de Responsabilidade Serrana

O **STRS** é uma aplicação desktop desenvolvida para automatizar a geração de Termos de Responsabilidade de equipamentos (empréstimos de aparelhos). O sistema gera documentos em PDF seguindo o padrão de relatórios do GLPI, garantindo conformidade e organização no controle de ativos de TI.

## 🚀 Funcionalidades

- **Interface Moderna**: Desenvolvida com tecnologias web (HTML/CSS/JS) integrada ao Python via `pywebview`.
- **Geração de PDF**: Emissão instantânea de termos com tabelas de metadados, cláusulas legais e campos de assinatura.
- **Padrão GLPI**: Layout idêntico aos chamados do GLPI para facilitar a integração visual com processos já existentes.
- **Máscaras Automáticas**: Campos como CPF possuem formatação automática para evitar erros.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **pywebview**: Para a camada de interface desktop.
- **fpdf2**: Motor de geração de documentos PDF.
- **HTML5/CSS3/JS**: Para o design premium e responsivo.

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/controle_termos.git
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Como Usar

Para iniciar a aplicação, execute o comando:
```bash
python main.py
```

Preencha os dados do colaborador e do equipamento no formulário e clique em **"Gerar Termo de Responsabilidade"**. O PDF será gerado na raiz do projeto e aberto automaticamente.

---
Desenvolvido para **Serrana Distribuidora**.
