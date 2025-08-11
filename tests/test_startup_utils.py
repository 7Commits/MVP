import logging

from utils.startup_utils import setup_logging, initialize_database, load_default_config
from utils.openai_client import DEFAULT_MODEL, DEFAULT_ENDPOINT


def test_setup_logging_creates_file(tmp_path):
    log_file = tmp_path / "app.log"
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    setup_logging(log_file=log_file)
    logging.getLogger().info("hello")
    assert log_file.exists()
    assert "hello" in log_file.read_text()


def test_initialize_database_calls_init_db(monkeypatch, mocker):
    dummy_engine = mocker.MagicMock()
    monkeypatch.setattr(
        initialize_database.__globals__["DatabaseEngine"],
        "instance",
        classmethod(lambda cls: dummy_engine),
    )
    initialize_database()
    dummy_engine.init_db.assert_called_once()


def test_load_default_config_returns_expected(monkeypatch, tmp_path):
    db_cfg = tmp_path / "db.config"
    db_cfg.write_text("[mysql]\nuser=u\npassword=p\nhost=h\ndatabase=d\n")
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    config = load_default_config()
    assert config == {
        "api_key": "key",
        "endpoint": DEFAULT_ENDPOINT,
        "model": DEFAULT_MODEL,
        "temperature": 0.0,
        "max_tokens": 1000,
    }
