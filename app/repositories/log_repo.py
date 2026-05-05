import logging
from app.repositories.base import BaseRepository


class LogRepository(BaseRepository):
    """Responsável por toda escrita na tabela de auditoria (logs)."""

    def registrar_log(self, acao, entidade, entidade_id, usuario, detalhes=""):
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO logs (acao, entidade, entidade_id, usuario, detalhes) VALUES (?, ?, ?, ?, ?)",
                    (acao, entidade, str(entidade_id), usuario, detalhes),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao registrar log: {e}")

    def get_all(self, limit=50):
        """Busca os logs mais recentes para auditoria."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM logs ORDER BY criado_em DESC LIMIT ?", (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao buscar logs: {e}")
            return []
