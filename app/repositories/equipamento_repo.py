import logging
from app.repositories.base import BaseRepository


class EquipamentoRepository(BaseRepository):
    """Operações sobre a tabela equipamentos (estoque e checagem de IMEI)."""

    def get_all(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM equipamentos ORDER BY criado_em DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro ao buscar estoque: {e}")
            return []

    def add(self, data):
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO equipamentos (imei, marca, modelo, categoria, valor, status)
                       VALUES (?, ?, ?, ?, ?, 'Disponível')
                       ON CONFLICT(imei) DO UPDATE SET
                           marca=excluded.marca, modelo=excluded.modelo,
                           categoria=excluded.categoria, valor=excluded.valor""",
                    (data["imei"], data["marca"], data["modelo"], data["categoria"], data["valor"]),
                )
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Erro ao adicionar ao estoque: {e}")
            return False

    def delete(self, imei):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM termos WHERE imei = ?", (imei,))
                if cursor.fetchone()[0] > 0:
                    return False, "Este item possui histórico e não pode ser deletado."
                cursor.execute("DELETE FROM equipamentos WHERE imei = ?", (imei,))
                conn.commit()
                return True, "Item removido."
        except Exception as e:
            return False, str(e)

    def check_imei_active(self, imei):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                result = {"active": False, "equipamento": None}

                cursor.execute(
                    "SELECT marca, modelo, valor FROM equipamentos WHERE imei = ?", (imei,)
                )
                equip_row = cursor.fetchone()
                if equip_row:
                    result["equipamento"] = {
                        "marca": equip_row["marca"],
                        "modelo": equip_row["modelo"],
                        "valor": equip_row["valor"],
                    }

                cursor.execute(
                    """SELECT t.id, c.nome FROM termos t
                       JOIN colaboradores c ON t.cpf = c.cpf
                       WHERE t.imei = ? AND t.status = 'Ativo'""",
                    (imei,),
                )
                row = cursor.fetchone()
                if row:
                    result["active"] = True
                    result["nome"] = row["nome"]
                    result["termo_id"] = row["id"]

                return result
        except Exception as e:
            logging.error(f"Erro ao checar IMEI: {e}")
            return {"active": False, "equipamento": None}

    def get_history(self, imei):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT t.*, c.nome, c.cpf FROM termos t
                       JOIN colaboradores c ON t.cpf = c.cpf
                       WHERE t.imei = ?
                       ORDER BY t.criado_em DESC""",
                    (imei,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Erro no histórico do equipamento: {e}")
            return []
