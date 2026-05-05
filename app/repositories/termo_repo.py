import logging
import os
from datetime import datetime
from app.repositories.base import BaseRepository


class TermoRepository(BaseRepository):
    """Operações sobre a tabela termos: criação, edição, histórico, baixa e chip."""

    # --- Consultas ---

    def get_history(
        self,
        filtro_cpf=None,
        filtro_imei=None,
        limit=10,
        offset=0,
        sort_by="id",
        sort_dir="DESC",
        filtro_nome=None,
        filtro_status=None,
        filtro_categoria=None,
        filtro_filial=None,
    ):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                sort_map = {
                    "colaborador": "c.nome",
                    "equipamento": "e.marca",
                    "entrega": "t.data_entrega",
                    "status": "t.status",
                    "id": "t.id",
                }
                order_column = sort_map.get(sort_by, "t.id")
                order_direction = "ASC" if sort_dir.upper() == "ASC" else "DESC"

                base_query = """
                    FROM termos t
                    JOIN colaboradores c ON t.cpf = c.cpf
                    JOIN equipamentos e ON t.imei = e.imei
                    WHERE 1=1
                """
                params = []

                if filtro_nome:
                    base_query += " AND c.nome LIKE ?"
                    params.append(f"%{filtro_nome}%")
                if filtro_cpf:
                    cpf_limpo = "".join(filter(str.isdigit, str(filtro_cpf)))
                    if cpf_limpo:
                        base_query += " AND c.cpf LIKE ?"
                        params.append(f"%{cpf_limpo}%")
                if filtro_imei:
                    base_query += " AND e.imei LIKE ?"
                    params.append(f"%{filtro_imei}%")
                if filtro_status:
                    base_query += " AND t.status = ?"
                    params.append(filtro_status)
                if filtro_categoria:
                    base_query += " AND e.categoria = ?"
                    params.append(filtro_categoria)
                if filtro_filial:
                    base_query += " AND t.filial = ?"
                    params.append(filtro_filial)

                cursor.execute(f"SELECT COUNT(*) {base_query}", params)
                total_records = cursor.fetchone()[0]

                data_query = f"""
                    SELECT
                        t.id, c.nome, c.cpf, c.cargo,
                        e.marca, e.modelo, e.imei, e.valor, e.categoria,
                        t.tecnico, t.data_entrega, t.data_baixa, t.status,
                        t.caminho_pdf, t.descricao, t.condicao_entrega,
                        t.condicao_devolucao, t.chip, t.filial,
                        (SELECT COUNT(*) FROM termos WHERE cpf = c.cpf) as total_colaborador,
                        (SELECT COUNT(*) FROM termos WHERE imei = e.imei) as total_equipamento
                    {base_query}
                    ORDER BY {order_column} {order_direction}
                    LIMIT ? OFFSET ?
                """
                cursor.execute(data_query, params + [limit, offset])
                records = [dict(row) for row in cursor.fetchall()]
                return {"data": records, "total_records": total_records}
        except Exception as e:
            logging.error(f"Erro ao buscar histórico: {e}")
            return {"data": [], "total_records": 0}

    def get_dashboard_stats(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM termos")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(DISTINCT cpf) FROM termos WHERE status = 'Ativo'")
                active_users = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM termos WHERE status = 'Ativo'")
                active_devices = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM termos WHERE status = 'Finalizado'")
                finished = cursor.fetchone()[0]
                return {
                    "total_terms": total,
                    "active_users": active_users,
                    "active_devices": active_devices,
                    "finished_terms": finished,
                }
        except Exception as e:
            logging.error(f"Erro nos stats: {e}")
            return {"total_terms": 0, "active_users": 0, "active_devices": 0, "finished_terms": 0}

    # --- Escrita ---

    def salvar(self, data, pdf_path):
        """Insere um novo termo garantindo que o equipamento esteja disponível."""
        try:
            data["cpf"] = "".join(filter(str.isdigit, str(data["cpf"])))
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Checagem de Concorrência (Safety Check)
                # Verifica se o equipamento já não foi pego por outro técnico no último segundo
                cursor.execute("SELECT status FROM equipamentos WHERE imei = ?", (data["imei"],))
                equip = cursor.fetchone()
                
                if equip and equip["status"] == 'Em Uso':
                    raise Exception("Este equipamento já está registrado como 'Em Uso'. Alguém pode ter finalizado o registro antes de você.")

                # 2. Upsert do Colaborador
                cursor.execute(
                    "INSERT INTO colaboradores (cpf, nome, cargo) VALUES (?, ?, ?) "
                    "ON CONFLICT(cpf) DO UPDATE SET nome=excluded.nome, cargo=excluded.cargo",
                    (data["cpf"], data["name"], data.get("cargo", "")),
                )

                # 3. Atualização do Equipamento para 'Em Uso' (Trava o recurso)
                cursor.execute(
                    "INSERT INTO equipamentos (imei, marca, modelo, valor, status) VALUES (?, ?, ?, ?, 'Em Uso') "
                    "ON CONFLICT(imei) DO UPDATE SET status='Em Uso', marca=excluded.marca, modelo=excluded.modelo, valor=excluded.valor",
                    (data["imei"], data["brand"], data["model"], data["value"]),
                )

                # 4. Inserção do Termo
                cursor.execute(
                    """INSERT INTO termos
                       (cpf, imei, tecnico, data_entrega, data_devolucao_prevista,
                        status, descricao, caminho_pdf, condicao_entrega, chip, filial)
                       VALUES (?, ?, ?, ?, ?, 'Ativo', ?, ?, ?, ?, ?)""",
                    (
                        data["cpf"], data["imei"], data["technician"],
                        data["delivery_date"], data["return_date"],
                        data["description"], pdf_path,
                        data.get("condicao_entrega", ""), data.get("chip", ""), data.get("filial", ""),
                    ),
                )
                
                novo_id = cursor.lastrowid
                conn.commit()
                return novo_id
        except sqlite3.IntegrityError:
            # Se cair aqui, o índice idx_termo_ativo barrou a duplicidade
            raise Exception("Erro de integridade: Já existe um termo ATIVO para este equipamento. Recarregue a página.")
        except Exception as e:
            logging.error(f"Erro ao salvar termo: {e}")
            raise

    def update_full(self, termo_id, data, new_pdf_path):
        """Atualiza todos os campos de um termo existente."""
        try:
            data["cpf"] = "".join(filter(str.isdigit, str(data["cpf"])))
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT caminho_pdf FROM termos WHERE id = ?", (termo_id,))
                row = cursor.fetchone()
                if row and row["caminho_pdf"] and os.path.exists(row["caminho_pdf"]):
                    try:
                        os.remove(row["caminho_pdf"])
                    except OSError as exc:
                        logging.warning(f"Não foi possível remover PDF antigo: {exc}")

                cursor.execute(
                    "INSERT INTO colaboradores (cpf, nome, cargo) VALUES (?, ?, ?) ON CONFLICT(cpf) DO UPDATE SET nome=excluded.nome, cargo=excluded.cargo",
                    (data["cpf"], data["name"], data.get("cargo", "")),
                )
                cursor.execute(
                    "INSERT INTO equipamentos (imei, marca, modelo, categoria, valor, status) VALUES (?, ?, ?, ?, ?, 'Em Uso') ON CONFLICT(imei) DO UPDATE SET marca=excluded.marca, modelo=excluded.modelo, categoria=excluded.categoria, valor=excluded.valor",
                    (data["imei"], data["brand"], data["model"], data.get("category", ""), data["value"]),
                )
                cursor.execute(
                    """UPDATE termos SET
                           cpf=?, imei=?, data_entrega=?, data_devolucao_prevista=?,
                           descricao=?, condicao_entrega=?, chip=?, filial=?, caminho_pdf=?
                       WHERE id=?""",
                    (
                        data["cpf"], data["imei"], data["delivery_date"], data["return_date"],
                        data["description"], data.get("condicao_entrega", ""),
                        data.get("chip", ""), data.get("filial", ""), new_pdf_path, termo_id,
                    ),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Erro ao atualizar termo: {e}")
            raise

    def dar_baixa(self, imei, data, usuario_logado="Sistema"):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute("SELECT id FROM termos WHERE imei = ? AND status = 'Ativo'", (imei,))
                termo = cursor.fetchone()
                termo_id = termo["id"] if termo else "Desconhecido"

                cursor.execute(
                    "UPDATE termos SET status='Finalizado', data_baixa=?, condicao_devolucao=? WHERE imei=? AND status='Ativo'",
                    (data_hoje, data.get("condicao", ""), imei),
                )
                cursor.execute(
                    "UPDATE equipamentos SET status='Disponível' WHERE imei=?", (imei,)
                )
                conn.commit()
                return cursor.rowcount > 0, termo_id
        except Exception as e:
            logging.error(f"Erro ao dar baixa: {e}")
            return False, None

    def update_chip(self, termo_id, novo_chip):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT chip FROM termos WHERE id = ?", (termo_id,))
                row = cursor.fetchone()
                chip_antigo = row["chip"] if row else ""
                cursor.execute("UPDATE termos SET chip=? WHERE id=?", (novo_chip, termo_id))
                conn.commit()
                return True, chip_antigo
        except Exception as e:
            logging.error(f"Erro ao atualizar chip: {e}")
            return False, None
