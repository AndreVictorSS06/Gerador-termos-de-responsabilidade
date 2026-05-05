import os
from app.database import DatabaseManager
from app.services.term_service import TermService


class Bridge:
    """
    Camada de comunicação entre o frontend (JS/PyWebView) e o backend Python.

    Responsabilidade única: expor métodos à API do PyWebView e delegar
    toda a lógica de negócio aos serviços e repositórios especializados.
    """

    def __init__(self):
        self._db = DatabaseManager()
        self._window = None

        logo_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui", "assets")
        self._term_service = TermService(
            termo_repo=self._db.termos,
            log_repo=self._db.logs,
            logo_dir=logo_dir,
        )

    def set_window(self, window):
        self._window = window

    def get_logged_user(self):
        # TODO: substituir por um AuthService com login real (item #4 do backlog)
        return {"name": "André Victor", "role": "Sênior"}

    # --- HISTÓRICO E TERMOS ---

    def get_history(self, cpf_filter=None, imei_filter=None, limit=10, offset=0,
                    sort_by="id", sort_dir="DESC", name_filter=None,
                    status_filter=None, category_filter=None, filial_filter=None):
        print(f"[API] get_history: cpf={cpf_filter}, imei={imei_filter}, sort={sort_by} {sort_dir}")
        return self._db.termos.get_history(
            cpf_filter, imei_filter, limit, offset,
            sort_by, sort_dir, name_filter, status_filter, category_filter, filial_filter,
        )

    def get_dashboard_stats(self):
        return self._db.termos.get_dashboard_stats()

    def get_logs(self):
        return self._db.logs.get_all()

    def get_colaborador_history(self, cpf):
        return self._db.colaboradores.get_history(cpf)

    def get_colaborador_by_cpf(self, cpf):
        return self._db.colaboradores.get_by_cpf(cpf)

    def get_equipamento_history(self, imei):
        return self._db.equipamentos.get_history(imei)

    def check_imei_active(self, imei):
        return self._db.equipamentos.check_imei_active(imei)

    def release_equipment(self, imei, data):
        try:
            logged_user = self.get_logged_user()
            success, termo_id = self._db.termos.dar_baixa(imei, data, logged_user["name"])
            if success:
                self._db.logs.registrar_log(
                    "DEVOLUCAO", "TERMO", termo_id, logged_user["name"],
                    f"Devolução do equipamento {imei}. Condição: {data.get('condicao', '')}",
                )
            return {"success": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_chip(self, termo_id, novo_chip):
        try:
            logged_user = self.get_logged_user()
            success, chip_antigo = self._db.termos.update_chip(termo_id, novo_chip)
            if success:
                self._db.logs.registrar_log(
                    "EDICAO_CHIP", "TERMO", termo_id, logged_user["name"],
                    f"Chip alterado de '{chip_antigo}' para '{novo_chip}'",
                )
            return {"success": success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- ESTOQUE / INVENTÁRIO ---

    def get_stock(self):
        return self._db.equipamentos.get_all()

    def add_to_stock(self, data):
        return {"success": self._db.equipamentos.add(data)}

    def delete_from_stock(self, imei):
        success, message = self._db.equipamentos.delete(imei)
        return {"success": success, "message": message}

    # --- GERAÇÃO DE PDF ---

    def open_pdf(self, path):
        if os.path.exists(path):
            os.startfile(path)
            return {"success": True}
        return {"success": False, "error": "Arquivo não encontrado."}

    def generate_term(self, data):
        """Cria um novo termo delegando ao TermService."""
        logged_user = self.get_logged_user()
        return self._term_service.generate(data, logged_user["name"])

    def edit_term(self, termo_id, data):
        """Edita um termo existente delegando ao TermService."""
        logged_user = self.get_logged_user()
        return self._term_service.edit(termo_id, data, logged_user["name"])
