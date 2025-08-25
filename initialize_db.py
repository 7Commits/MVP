import logging
from utils.startup_utils import setup_logging

logger = logging.getLogger(__name__)

try:
    from models.database import DatabaseEngine
except ModuleNotFoundError as exc:
    logger.error(
        "Modulo mancante. Installa le dipendenze con 'pip install -r requirements.txt'"
    )
    logger.error(f"Errore specifico: {exc}")
    raise exc

if __name__ == '__main__':
    setup_logging()
    logger.info("Inizializzazione del database...")
    try:
        DatabaseEngine.instance().init_db()
        logger.info("Database inizializzato con successo!")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}")
        logger.exception("Traccia dettagliata:")
