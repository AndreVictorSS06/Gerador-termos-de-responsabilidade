import sqlite3
import os
import logging

from app.repositories.log_repo import LogRepository
from app.repositories.colaborador_repo import ColaboradorRepository
from app.repositories.equipamento_repo import EquipamentoRepository
from app.repositories.termo_repo import TermoRepository


class DatabaseManager:
    """
    Gerenciador de conexão e migração do banco de dados SQLite.

    Responsabilidades (únicas):
    - Prover get_connection() para os repositórios
    - Inicializar o schema (init_db)
    - Aplicar migrações não-destrutivas (_migrate_db)
    - Expor os repositórios como atributos públicos
    """

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "banco_dados.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path

        self.init_db()
        self._migrate_db()

        # Repositórios — cada um tem sua responsabilidade única
        self.logs = LogRepository(self)
        self.colaboradores = ColaboradorRepository(self)
        self.equipamentos = EquipamentoRepository(self)
        self.termos = TermoRepository(self)

    def get_connection(self):
        """Retorna uma conexão SQLite com row_factory para acesso por nome de coluna."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS colaboradores (
                    cpf  TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    cargo TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipamentos (
                    imei       TEXT PRIMARY KEY,
                    marca      TEXT NOT NULL,
                    modelo     TEXT NOT NULL,
                    categoria  TEXT,
                    valor      REAL,
                    status     TEXT DEFAULT 'Disponível',
                    criado_em  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS termos (
                    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf                     TEXT,
                    imei                    TEXT,
                    tecnico                 TEXT,
                    data_entrega            TEXT,
                    data_devolucao_prevista TEXT,
                    data_baixa              TEXT,
                    status                  TEXT DEFAULT 'Ativo',
                    descricao               TEXT,
                    caminho_pdf             TEXT,
                    condicao_entrega        TEXT,
                    condicao_devolucao      TEXT,
                    chip                    TEXT,
                    filial                  TEXT,
                    criado_em               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cpf)  REFERENCES colaboradores (cpf),
                    FOREIGN KEY (imei) REFERENCES equipamentos (imei)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    acao        TEXT NOT NULL,
                    entidade    TEXT NOT NULL,
                    entidade_id TEXT NOT NULL,
                    usuario     TEXT NOT NULL,
                    detalhes    TEXT,
                    criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índice Único Filtrado: Garante que um IMEI só tenha UM termo ATIVO por vez.
            # Isso impede bugs de concorrência onde dois usuários tentam registrar o mesmo aparelho simultaneamente.
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_termo_ativo 
                ON termos(imei) 
                WHERE status = 'Ativo'
            """)

            conn.commit()

    def _migrate_db(self):
        """Adiciona colunas novas a tabelas existentes sem apagar dados."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # colaboradores
                cursor.execute("PRAGMA table_info(colaboradores)")
                colab_cols = [r[1] for r in cursor.fetchall()]
                if "cargo" not in colab_cols:
                    cursor.execute("ALTER TABLE colaboradores ADD COLUMN cargo TEXT")

                # termos — renomear FKs antigas e adicionar colunas novas
                cursor.execute("PRAGMA table_info(termos)")
                termo_cols = [r[1] for r in cursor.fetchall()]

                if "colaborador_cpf" in termo_cols:
                    cursor.execute("ALTER TABLE termos RENAME COLUMN colaborador_cpf TO cpf")
                if "equipamento_imei" in termo_cols:
                    cursor.execute("ALTER TABLE termos RENAME COLUMN equipamento_imei TO imei")

                cursor.execute("PRAGMA table_info(termos)")
                termo_cols = [r[1] for r in cursor.fetchall()]

                for col in ("condicao_entrega", "condicao_devolucao", "chip", "filial"):
                    if col not in termo_cols:
                        cursor.execute(f"ALTER TABLE termos ADD COLUMN {col} TEXT")

                conn.commit()
        except Exception as e:
            logging.error(f"Erro na migração do banco: {e}")
