import logging
import runpy


def test_initialize_db_logs_success(mocker, caplog):
    mock_engine = mocker.MagicMock()
    mocker.patch("models.database.DatabaseEngine.instance", return_value=mock_engine)
    mocker.patch("utils.startup_utils.setup_logging")
    caplog.set_level(logging.INFO)

    runpy.run_module("initialize_db", run_name="__main__")

    mock_engine.init_db.assert_called_once_with()
    assert any(
        "Database inizializzato con successo" in record.message for record in caplog.records
    )


def test_initialize_db_logs_error(mocker, caplog):
    mock_engine = mocker.MagicMock()
    mock_engine.init_db.side_effect = Exception("boom")
    mocker.patch("models.database.DatabaseEngine.instance", return_value=mock_engine)
    mocker.patch("utils.startup_utils.setup_logging")
    caplog.set_level(logging.ERROR)

    runpy.run_module("initialize_db", run_name="__main__")

    mock_engine.init_db.assert_called_once_with()
    assert any(
        "Errore durante l'inizializzazione del database" in record.message
        for record in caplog.records
    )
