import logging
from app.repositories.base import BaseRepository


class ColaboradorRepository(BaseRepository):
    """Operações de leitura e escrita sobre a tabela colaboradores."""

    def get_by_cpf(self, cpf):
        try:
            cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nome, cargo FROM colaboradores WHERE cpf = ?", (cpf_limpo,))
                row = cursor.fetchone()
                if row:
                    return {"success": True, "nome": row["nome"], "cargo": row["cargo"]}
                return {"success": False}
        except Exception as e:
            logging.error(f"Erro ao buscar colaborador por CPF: {e}")
            return {"success": False}

    def get_history(self, cpf):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.*, e.marca, e.modelo, e.imei
                       FROM termos t
                       JOIN equipamentos e ON t.imei = e.imei
                       WHERE t.cpf = ?
                       ORDER BY t.criado_em DESC""",
                    (cpf,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro no histórico do colaborador: {e}")
            return []
