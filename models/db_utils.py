import logging

import configparser
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
logger = logging.getLogger(__name__)


def _ensure_database(cfg):
    """Crea il database di destinazione se non esiste."""
    root_url = (
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg.get('port', 3306)}"
    )
    engine = create_engine(root_url, isolation_level="AUTOCOMMIT")
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`"))
    except Exception as exc:
        logger.exception(
            "Impossibile creare il database '%s' sull'host '%s' con l'utente '%s'",
            cfg.get('database'),
            cfg.get('host'),
            cfg.get('user'),
        )
        raise RuntimeError(
            f"Impossibile creare il database '{cfg.get('database')}' sull'host '{cfg.get('host')}' per l'utente '{cfg.get('user')}'. "
            "Il server del database potrebbe essere irraggiungibile, le credenziali potrebbero non essere valide "
            "oppure l'utente potrebbe non avere privilegi sufficienti.",
        ) from exc


Base = declarative_base()
_engine = None
_SessionFactory = None


def get_engine():
    """Restituisce un'istanza di motore SQLAlchemy."""
    global _engine
    if _engine is None:
        config = configparser.ConfigParser()
        root = Path(__file__).resolve().parent.parent
        cfg_path = root / 'db.config'
        if not cfg_path.exists():
            cfg_path = root / 'db.config.example'
        config.read(cfg_path)
        cfg = config['mysql']
        _ensure_database(cfg)
        url = (
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg.get('port', 3306)}/{cfg['database']}"
        )
        _engine = create_engine(
            url,
            pool_pre_ping=True,  # Verifica che le connessioni siano attive
            pool_recycle=3600,   # Ricicla le connessioni inattive per evitare timeout
        )
    return _engine


def get_session():
    """Restituisce una nuova sessione ORM."""
    global _SessionFactory
    engine = get_engine()
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=engine)
    return _SessionFactory()


def init_db():
    """Crea le tabelle necessarie se non esistono."""
    engine = get_engine()
    # Assicura che tutti i modelli ORM siano registrati
    import models.orm_models  # noqa: F401
    Base.metadata.create_all(engine)
