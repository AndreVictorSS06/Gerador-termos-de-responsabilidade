# 📑 STRS - Sistema de Termos de Responsabilidade

O **STRS** é uma aplicação desktop profissional desenvolvida para automatizar a gestão e emissão de Termos de Responsabilidade para empréstimos de ativos de TI. Inspirado no padrão de relatórios do GLPI, o sistema oferece uma solução completa para controle de inventário, conformidade jurídica e auditoria de ações.

---

## ✨ Funcionalidades Principais

- **🛡️ Auditoria Completa**: Aba exclusiva para administradores rastrearem todas as ações realizadas (criações, edições, devoluções e trocas de chip).
- **📊 Dashboard de Gestão**: Indicadores em tempo real sobre o total de termos, equipamentos em uso e usuários ativos.
- **📁 Dossiê 360º**: Histórico individualizado por colaborador e por equipamento (IMEI/Serial), permitindo rastreabilidade total do ciclo de vida do ativo.
- **📄 Geração de PDF Premium**: Emissão de termos em PDF com layout profissional, cláusulas legais automatizadas e metadados de chamado.
- **⚡ Interface Moderna**: Experiência de usuário fluida com tecnologias web (HTML/CSS/JS) rodando nativamente via `pywebview`.
- **🔍 Busca e Filtros Avançados**: Localização instantânea de registros por CPF, IMEI, Nome, Filial ou Status.

---

## 🏗️ Arquitetura do Sistema

O projeto segue padrões avançados de desenvolvimento para garantir manutenção fácil e escalabilidade:

- **Service Layer**: Lógica de negócio orquestrada centralmente (ex: `TermService`).
- **Repository Pattern**: Camada de acesso a dados isolada, garantindo integridade nas operações do banco de dados.
- **SQLite Engine**: Banco de dados relacional local, rápido e sem necessidade de servidores externos.
- **Clean Interface**: Separação total entre a lógica Python (Backend) e a interface visual (Frontend).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **pywebview**: Container desktop para a interface.
- **fpdf2**: Motor de geração de documentos PDF de alta performance.
- **SQLite3**: Banco de dados local.
- **Google Fonts (Inter)**: Tipografia moderna e legível.

---

## 📦 Instalação e Uso

1. **Ativar o Ambiente Virtual:**
   ```bash
   .\venv\Scripts\activate
   ```

2. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar a Aplicação:**
   ```bash
   python main.py
   ```

---

## 📂 Estrutura de Pastas

- `/app`: Cérebro da aplicação (Serviços, Repositórios e Banco de Dados).
- `/gui`: Interface visual (HTML, CSS, JS e Assets).
- `/data`: Armazenamento de PDFs gerados e arquivo do Banco de Dados.

---
Desenvolvido por André Victor para **Grupo Serrana**.
