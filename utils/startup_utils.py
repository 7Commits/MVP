import logging
import os

from pathlib import Path
from typing import TypedDict

from models.database import DatabaseEngine
from utils.openai_client import DEFAULT_MODEL, DEFAULT_ENDPOINT

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO, log_file: str | Path | None = None) -> None:
    """Configura il logger radice con un formato di base.

    Se viene fornito ``log_file`` i log vengono scritti anche su tale file.
    """
    # ``logging.basicConfig`` non accetta un dizionario tipato con ``**`` in modo
    # sicuro per mypy. Passiamo quindi gli argomenti esplicitamente in modo da
    # evitare problemi di tipizzazione.
    filename = str(log_file) if log_file is not None else None
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=filename,
    )


def initialize_database() -> None:
    """Inizializza il database dell'applicazione."""
    DatabaseEngine.instance().init_db()


class DefaultConfig(TypedDict):
    """Configurazione di default per il client OpenAI."""

    api_key: str
    endpoint: str
    model: str
    temperature: float
    max_tokens: int


def load_default_config() -> DefaultConfig:
    """Restituisce la configurazione API di default."""
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "endpoint": DEFAULT_ENDPOINT,
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000,
    }
