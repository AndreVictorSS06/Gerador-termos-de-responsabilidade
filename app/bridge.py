import os
import threading
from datetime import datetime
from app.database import DatabaseManager
from app.services.pdf_service import PDFService

class Bridge:
    def __init__(self):
        self._db = DatabaseManager()
        self._window = None

    def _get_window(self):
        return self._window

    def set_window(self, window):
        self._window = window

    def get_history(self, cpf_filter=None, imei_filter=None, page=1):
        limit = 10
        offset = (page - 1) * limit
        return self._db.get_history(cpf_filter, imei_filter, limit, offset)

    def get_dashboard_stats(self):
        return self._db.get_dashboard_stats()

    def get_colaborador_history(self, cpf):
        return self._db.get_colaborador_history(cpf)

    def get_equipamento_history(self, imei):
        return self._db.get_equipamento_history(imei)

    def open_pdf(self, path):
        if os.path.exists(path):
            os.startfile(path)
            return {"success": True}
        return {"success": False, "error": "Arquivo não encontrado."}

    def release_equipment(self, imei):
        success = self._db.dar_baixa_equipamento(imei)
        return {"success": success}

    def generate_term(self, data):
        threading.Thread(target=self._worker_generate, args=(data,), daemon=True).start()
        return {"success": True}

    def _worker_generate(self, data):
        try:
            filename = f"Termo_{data['name'].replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.pdf"
            output_path = os.path.join(os.getcwd(), 'data', 'termos', filename)
            self._db.salvar_termo(data, output_path)
            PDFService.generate(data, output_path)
            os.startfile(output_path)
            
            win = self._get_window()
            if win:
                win.evaluate_js(f"onTermGenerated(true, '{filename}')")
                
        except Exception as e:
            win = self._get_window()
            if win:
                error_msg = str(e).replace("'", "\\'").replace("\n", " ")
                win.evaluate_js(f"onTermGenerated(false, '{error_msg}')")
