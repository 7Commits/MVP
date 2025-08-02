import logging
from logging_config import setup_logging

try:
    from models.db_utils import init_db
except ModuleNotFoundError as exc:
    logging.error(
        "Modulo mancante. Installa le dipendenze con 'pip install -r requirements.txt'"
    )
    logging.error(f"Errore specifico: {exc}")
    raise exc

if __name__ == '__main__':
    setup_logging()
    logging.info("Inizializzazione del database in corso...")
    try:
        init_db()
        logging.info("Database inizializzato con successo!")
    except Exception as e:
        logging.error(f"Errore durante l'inizializzazione del database: {e}")
        logging.exception("Traceback dettagliato:")
