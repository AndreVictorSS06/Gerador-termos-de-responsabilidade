import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/banco_dados.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        # timeout=30 ajuda a evitar erros de "database is locked" com 2 usuários
        conn = sqlite3.connect(self.db_path, timeout=30)
        # Habilita o retorno em formato de dicionário
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Habilita o modo WAL para melhor performance multiusuário
            cursor.execute('PRAGMA journal_mode = WAL')
            
            # Tabela de Colaboradores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS colaboradores (
                    cpf TEXT PRIMARY KEY,
                    nome TEXT NOT NULL
                )
            ''')
            
            # Tabela de Equipamentos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipamentos (
                    imei TEXT PRIMARY KEY,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    valor TEXT
                )
            ''')
            
            # Tabela de Termos (Transacional)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS termos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    colaborador_cpf TEXT,
                    equipamento_imei TEXT,
                    tecnico TEXT,
                    data_entrega TEXT,
                    data_devolucao_prevista TEXT,
                    data_baixa TEXT,
                    status TEXT DEFAULT 'Ativo',
                    descricao TEXT,
                    caminho_pdf TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (colaborador_cpf) REFERENCES colaboradores (cpf),
                    FOREIGN KEY (equipamento_imei) REFERENCES equipamentos (imei)
                )
            ''')
            conn.commit()

    def get_history(self, filtro_cpf=None, filtro_imei=None, limit=10, offset=0):
        """Retorna a lista de termos com filtros, contadores e paginação."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT 
                        t.id, c.nome, c.cpf, e.marca, e.modelo, e.imei, 
                        t.tecnico, t.data_entrega, t.data_baixa, t.status, t.caminho_pdf,
                        (SELECT COUNT(*) FROM termos WHERE colaborador_cpf = c.cpf) as total_colaborador,
                        (SELECT COUNT(*) FROM termos WHERE equipamento_imei = e.imei) as total_equipamento
                    FROM termos t
                    JOIN colaboradores c ON t.colaborador_cpf = c.cpf
                    JOIN equipamentos e ON t.equipamento_imei = e.imei
                    WHERE 1=1
                '''
                params = []
                if filtro_cpf:
                    query += " AND c.cpf LIKE ?"
                    params.append(f"%{filtro_cpf}%")
                if filtro_imei:
                    query += " AND e.imei LIKE ?"
                    params.append(f"%{filtro_imei}%")
                
                query += " ORDER BY t.criado_em DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []

    def get_dashboard_stats(self):
        """Retorna estatísticas para o dashboard."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                stats = {}
                
                # Total de Termos
                cursor.execute("SELECT COUNT(*) FROM termos")
                stats['total_terms'] = cursor.fetchone()[0]
                
                # Colaboradores com Ativos (Unique)
                cursor.execute("SELECT COUNT(DISTINCT colaborador_cpf) FROM termos WHERE status = 'Ativo'")
                stats['active_users'] = cursor.fetchone()[0]
                
                # Equipamentos em Campo
                cursor.execute("SELECT COUNT(*) FROM termos WHERE status = 'Ativo'")
                stats['active_devices'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            print(f"Erro ao buscar stats: {e}")
            return {'total_terms': 0, 'active_users': 0, 'active_devices': 0}

    def get_colaborador_history(self, cpf):
        """Busca todos os termos de um colaborador específico."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT t.*, e.marca, e.modelo, e.imei
                    FROM termos t
                    JOIN equipamentos e ON t.equipamento_imei = e.imei
                    WHERE t.colaborador_cpf = ?
                    ORDER BY t.criado_em DESC
                '''
                cursor.execute(query, (cpf,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception: return []

    def get_equipamento_history(self, imei):
        """Busca todos os colaboradores que já usaram este equipamento."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT t.*, c.nome, c.cpf
                    FROM termos t
                    JOIN colaboradores c ON t.colaborador_cpf = c.cpf
                    WHERE t.equipamento_imei = ?
                    ORDER BY t.criado_em DESC
                '''
                cursor.execute(query, (imei,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception: return []

    def dar_baixa_equipamento(self, imei):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M')
            cursor.execute('''
                UPDATE termos 
                SET status = 'Finalizado', data_baixa = ? 
                WHERE equipamento_imei = ? AND status = 'Ativo'
            ''', (data_hoje, imei))
            conn.commit()
            return cursor.rowcount > 0

    def salvar_termo(self, data, pdf_path):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Baixa automática no anterior
            self.dar_baixa_equipamento(data['imei'])

            # 1. Upsert no Colaborador
            cursor.execute('''
                INSERT INTO colaboradores (cpf, nome) 
                VALUES (?, ?)
                ON CONFLICT(cpf) DO UPDATE SET nome=excluded.nome
            ''', (data['cpf'], data['name']))
            
            # 2. Upsert no Equipamento
            cursor.execute('''
                INSERT INTO equipamentos (imei, marca, modelo, valor) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(imei) DO UPDATE SET 
                    marca=excluded.marca, 
                    modelo=excluded.modelo, 
                    valor=excluded.valor
            ''', (data['imei'], data['brand'], data['model'], data['value']))
            
            # 3. Registrar o novo Termo Ativo
            cursor.execute('''
                INSERT INTO termos (
                    colaborador_cpf, equipamento_imei, tecnico, data_entrega, 
                    data_devolucao_prevista, status, descricao, caminho_pdf
                ) VALUES (?, ?, ?, ?, ?, 'Ativo', ?, ?)
            ''', (
                data['cpf'], 
                data['imei'], 
                data['technician'],
                data['delivery_date'], 
                data['return_date'], 
                data['description'],
                pdf_path
            ))
            conn.commit()
