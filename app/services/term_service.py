import os
from datetime import datetime
from app.services.pdf_service import PDFService


class TermService:
    """
    Orquestra a criação e edição de Termos de Responsabilidade.

    Responsabilidades:
    - Construir o payload padronizado a partir dos dados brutos do formulário (#2)
    - Coordenar banco de dados, geração de PDF e abertura do arquivo (#1)
    - Registrar log de auditoria após cada operação
    """

    _TERM_FIELDS = [
        "name", "cpf", "brand", "model", "imei", "value",
        "delivery_date", "return_date", "description", "category",
        "condicao_entrega", "chip", "cargo", "filial",
    ]

    def __init__(self, termo_repo, log_repo, logo_dir: str):
        self._termos = termo_repo
        self._logs = log_repo
        self._logo_dir = logo_dir

    # --- Método privado: resolve o item #2 (DRY no payload) ---
    def _build_payload(self, data: dict, technician: str) -> dict:
        """Constrói o payload padronizado, garantindo que o técnico vem do sistema."""
        return {
            "technician": technician,
            **{field: data.get(field, "") for field in self._TERM_FIELDS},
        }

    def _get_output_path(self, name: str, prefix: str = "Termo", subdir: str = "") -> str:
        """Resolve o caminho do PDF organizando em subpastas se necessário."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "data", "termos", subdir)
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{prefix}_{name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.pdf"
        return os.path.join(output_dir, filename)

    # --- Operações públicas ---

    def generate(self, data: dict, technician: str) -> dict:
        """Cria um novo termo: persiste no banco, gera o PDF (pasta 'novos') e abre-o."""
        try:
            payload = self._build_payload(data, technician)
            output_path = self._get_output_path(payload["name"], subdir="novos")

            novo_id = self._termos.salvar(payload, output_path)
            
            # Adiciona o ID gerado pelo banco ao payload para aparecer no PDF
            payload["id"] = novo_id

            PDFService.generate(payload, output_path, logo_dir=self._logo_dir)
            os.startfile(output_path)

            self._logs.registrar_log(
                "CRIACAO", "TERMO", novo_id, technician,
                f"Termo gerado para {payload['name']} (CPF: {payload['cpf']}) "
                f"- Equipamento: {payload['model']} (IMEI: {payload['imei']})",
            )
            return {"success": True, "message": os.path.basename(output_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit(self, termo_id: int, data: dict, technician: str) -> dict:
        """Edita um termo: atualiza o banco e regenera o PDF (pasta 'editados')."""
        try:
            payload = self._build_payload(data, technician)
            
            # Adiciona o ID existente ao payload
            payload["id"] = termo_id

            output_path = self._get_output_path(payload["name"], prefix="Termo_Editado", subdir="editados")

            self._termos.update_full(termo_id, payload, output_path)
            PDFService.generate(payload, output_path, logo_dir=self._logo_dir)

            self._logs.registrar_log(
                "EDICAO_COMPLETA", "TERMO", termo_id, technician,
                "Termo atualizado completamente. Arquivo PDF recriado na pasta de editados.",
            )
            return {"success": True, "message": os.path.basename(output_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}
