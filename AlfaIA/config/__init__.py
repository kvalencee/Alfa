
# =============================================================================
# AlfaIA/config/__init__.py - Inicialización del paquete de configuración
# =============================================================================

from .settings import Settings
from .database_config import DatabaseConfig
from .nlp_config import NLPConfig

# Instancias globales
settings = Settings()
db_config = DatabaseConfig()
nlp_config = NLPConfig()

__all__ = ['Settings', 'DatabaseConfig', 'NLPConfig', 'settings', 'db_config', 'nlp_config']