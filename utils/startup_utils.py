import logging
import os

from models.database import DatabaseEngine
from utils.openai_client import DEFAULT_MODEL, DEFAULT_ENDPOINT

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configura il logger radice con un formato di base."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def initialize_database() -> None:
    """Inizializza il database dell'applicazione."""
    DatabaseEngine.instance().init_db()


def load_default_config() -> dict:
    """Restituisce la configurazione API di default."""
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINT,
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000,
    }
