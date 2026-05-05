class BaseRepository:
    """Classe base que provê acesso à conexão via DatabaseManager."""

    def __init__(self, db_manager):
        self._db = db_manager

    def get_connection(self):
        return self._db.get_connection()
