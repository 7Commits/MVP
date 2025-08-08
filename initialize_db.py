import logging
from controllers.startup_controller import setup_logging

logger = logging.getLogger(__name__)

try:
    from models.database import init_db
except ModuleNotFoundError as exc:
    logger.error(
        "Modulo mancante. Installa le dipendenze con 'pip install -r requirements.txt'"
    )
    logger.error(f"Errore specifico: {exc}")
    raise exc

if __name__ == '__main__':
    setup_logging()
    logger.info("Inizializzazione del database in corso...")
    try:
        init_db()
        logger.info("Database inizializzato con successo!")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}")
        logger.exception("Traceback dettagliato:")
