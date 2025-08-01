import configparser
from pathlib import Path
from sqlalchemy import create_engine, text


def _ensure_database(cfg):
    """Create the target database if it does not exist."""
    root_url = (
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg.get('port', 3306)}"
    )
    engine = create_engine(root_url, isolation_level="AUTOCOMMIT")
    with engine.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}`"))

_engine = None


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


def init_db():
    """Crea le tabelle necessarie se non esistono."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """CREATE TABLE IF NOT EXISTS questions (
                    id VARCHAR(36) PRIMARY KEY,
                    domanda TEXT,
                    risposta_attesa TEXT,
                    categoria TEXT
                )"""
            )
        )
        conn.execute(
            text(
                """CREATE TABLE IF NOT EXISTS question_sets (
                    id VARCHAR(36) PRIMARY KEY,
                    name TEXT
                )"""
            )
        )
        conn.execute(
            text(
                """CREATE TABLE IF NOT EXISTS question_set_questions (
                    set_id VARCHAR(36),
                    question_id VARCHAR(36),
                    PRIMARY KEY (set_id, question_id)
                )"""
            )
        )
        conn.execute(
            text(
                """CREATE TABLE IF NOT EXISTS test_results (
                    id VARCHAR(36) PRIMARY KEY,
                    set_id VARCHAR(36),
                    timestamp TEXT,
                    results JSON
                )"""
            )
        )
        conn.execute(
            text(
                """CREATE TABLE IF NOT EXISTS api_presets (
                    id VARCHAR(36) PRIMARY KEY,
                    name TEXT,
                    provider_name TEXT,
                    endpoint TEXT,
                    api_key TEXT,
                    model TEXT,
                    temperature FLOAT,
                    max_tokens INT
                )"""
            )
        )

