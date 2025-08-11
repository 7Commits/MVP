import pytest
from types import SimpleNamespace

from models import database
from models.database import DatabaseEngine


def test_get_engine_uses_config_and_create_engine(monkeypatch):
    DatabaseEngine._instance = None  # ensure fresh singleton
    db = DatabaseEngine.instance()
    db._engine = None  # type: ignore[attr-defined]
    fake_cfg = {'user': 'u', 'password': 'p', 'host': 'h', 'database': 'db'}
    monkeypatch.setattr(DatabaseEngine, '_load_config', lambda self: fake_cfg)
    called = {}

    def fake_ensure(self, cfg):
        called['ensure'] = cfg
    monkeypatch.setattr(DatabaseEngine, '_ensure_database', fake_ensure)
    fake_engine = SimpleNamespace()

    def fake_create_engine(url, pool_pre_ping=True, pool_recycle=3600):
        called['url'] = url
        return fake_engine
    monkeypatch.setattr(database, 'create_engine', fake_create_engine)

    engine = db.get_engine()
    assert engine is fake_engine
    assert called['ensure'] == fake_cfg
    assert 'mysql+pymysql://u:p@h:3306/db' in called['url']
    # second call should reuse same engine
    assert db.get_engine() is fake_engine


def test_ensure_database_error(monkeypatch):
    DatabaseEngine._instance = None
    db = DatabaseEngine.instance()

    class DummyEngine:
        def begin(self):
            raise Exception('boom')

    monkeypatch.setattr(database, 'create_engine', lambda *a, **k: DummyEngine())
    with pytest.raises(RuntimeError):
        db._ensure_database({
            'user': 'u',
            'password': 'p',
            'host': 'h',
            'database': 'd',
        })
