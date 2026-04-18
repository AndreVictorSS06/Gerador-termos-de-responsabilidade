import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
from datetime import datetime

# Carrega as configurações do arquivo .env
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.dbname = os.getenv("DB_NAME", "controle_termos")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASS", "")
        self.port = os.getenv("DB_PORT", "5432")
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            database=self.dbname,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def init_db(self):
        """Cria as tabelas se elas não existirem. 
        Nota: Você precisa criar o banco de dados 'controle_termos' manualmente no Postgres antes."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
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
                            id SERIAL PRIMARY KEY,
                            colaborador_cpf TEXT REFERENCES colaboradores(cpf),
                            equipamento_imei TEXT REFERENCES equipamentos(imei),
                            data_entrega TEXT,
                            data_devolucao_prevista TEXT,
                            data_baixa TEXT,
                            status TEXT DEFAULT 'Ativo',
                            descricao TEXT,
                            caminho_pdf TEXT,
                            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    conn.commit()
            print("Conexão com PostgreSQL estabelecida e tabelas verificadas.")
        except Exception as e:
            print(f"Erro ao conectar no PostgreSQL: {e}")
            print("Certifique-se de que o banco de dados existe e o serviço está rodando.")

    def dar_baixa_equipamento(self, imei):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M')
                    cursor.execute('''
                        UPDATE termos 
                        SET status = 'Finalizado', data_baixa = %s 
                        WHERE equipamento_imei = %s AND status = 'Ativo'
                    ''', (data_hoje, imei))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao dar baixa: {e}")
            return False

    def salvar_termo(self, data, pdf_path):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Baixa automática no anterior
                    self.dar_baixa_equipamento(data['imei'])

                    # 1. Upsert no Colaborador
                    cursor.execute('''
                        INSERT INTO colaboradores (cpf, nome) 
                        VALUES (%s, %s)
                        ON CONFLICT (cpf) DO UPDATE SET nome = EXCLUDED.nome
                    ''', (data['cpf'], data['name']))
                    
                    # 2. Upsert no Equipamento
                    cursor.execute('''
                        INSERT INTO equipamentos (imei, marca, modelo, valor) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (imei) DO UPDATE SET 
                            marca = EXCLUDED.marca, 
                            modelo = EXCLUDED.modelo, 
                            valor = EXCLUDED.valor
                    ''', (data['imei'], data['brand'], data['model'], data['value']))
                    
                    # 3. Registrar o novo Termo Ativo
                    cursor.execute('''
                        INSERT INTO termos (
                            colaborador_cpf, equipamento_imei, data_entrega, 
                            data_devolucao_prevista, status, descricao, caminho_pdf
                        ) VALUES (%s, %s, %s, %s, 'Ativo', %s, %s)
                    ''', (
                        data['cpf'], 
                        data['imei'], 
                        data['delivery_date'], 
                        data['return_date'], 
                        data['description'],
                        pdf_path
                    ))
                    conn.commit()
            print("Dados salvos no PostgreSQL com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar no PostgreSQL: {e}")
            raise e
