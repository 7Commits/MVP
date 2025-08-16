import logging
import threading
import configparser
from pathlib import Path
from typing import Mapping, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """Singleton thread-safe che fornisce l'engine del database e le sessioni."""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError(
                "DatabaseEngine è un singleton; usa DatabaseEngine.instance()"
            )
        return super().__new__(cls)

    def __init__(self) -> None:
        if self.__class__._instance is not None:
            raise RuntimeError(
                "DatabaseEngine è un singleton; usa DatabaseEngine.instance()"
            )
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._engine_lock = threading.Lock()
        self._session_lock = threading.Lock()

    @classmethod
    def instance(cls) -> "DatabaseEngine":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reimposta l'istanza singleton e svuota le risorse in cache."""
        with cls._instance_lock:
            if cls._instance is not None:
                with cls._instance._engine_lock:
                    if cls._instance._engine is not None:
                        cls._instance._engine.dispose()
                        cls._instance._engine = None
                with cls._instance._session_lock:
                    cls._instance._session_factory = None
            cls._instance = None

    def _load_config(self) -> Mapping[str, str]:
        config = configparser.ConfigParser()
        root = Path(__file__).resolve().parent.parent
        cfg_path = root / "db.config"
        if not cfg_path.exists():
            cfg_path = root / "db.config.example"
        config.read(cfg_path)
        return config["mysql"]

    def _ensure_database(self, cfg: Mapping[str, str]) -> None:
        """Crea il database di destinazione se non esiste già."""
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
                cfg.get("database"),
                cfg.get("host"),
                cfg.get("user"),
            )
            raise RuntimeError(
                (
                    f"Impossibile creare il database '{cfg.get('database')}' "
                    f"sull'host '{cfg.get('host')}' per l'utente '{cfg.get('user')}'. "
                    "Il server del database potrebbe non essere raggiungibile, le credenziali potrebbero essere errate "
                    "o l'utente potrebbe non avere privilegi sufficienti."
                )
            ) from exc

    def get_engine(self) -> Engine:
        if self._engine is None:
            with self._engine_lock:
                if self._engine is None:
                    cfg = self._load_config()
                    self._ensure_database(cfg)
                    url = (
                        f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg.get('port', 3306)}/{cfg['database']}"
                    )
                    self._engine = create_engine(
                        url,
                        pool_pre_ping=True,
                        pool_recycle=3600,
                    )
        assert self._engine is not None
        return self._engine

    def get_session(self) -> Session:
        if self._session_factory is None:
            with self._session_lock:
                if self._session_factory is None:
                    engine = self.get_engine()
                    self._session_factory = sessionmaker(bind=engine)
        assert self._session_factory is not None
        return self._session_factory()

    def init_db(self) -> None:
        engine = self.get_engine()
        import models.orm_models  # noqa: F401
        Base.metadata.create_all(engine)


class Base(DeclarativeBase):
    """Base class per i modelli dichiarativi SQLAlchemy."""
    pass

