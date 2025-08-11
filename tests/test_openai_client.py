import logging
import os
import sys
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.openai_client import (  # noqa: E402
    DEFAULT_MODEL,
    get_available_models_for_endpoint,
    get_openai_client,
)


def test_get_openai_client_no_api_key(caplog):
    caplog.set_level(logging.WARNING)
    client = get_openai_client("")
    assert client is None
    assert "Tentativo di creare client OpenAI senza chiave API." in caplog.text


def test_get_openai_client_uses_custom_base_url(mocker):
    mock_openai = mocker.patch("utils.openai_client.OpenAI")
    mock_client = mocker.MagicMock()
    mock_openai.return_value = mock_client

    result = get_openai_client("key", base_url="http://custom")

    mock_openai.assert_called_once_with(api_key="key", base_url="http://custom")
    assert result is mock_client


def test_get_available_models_returns_error_when_no_client(mocker):
    mocker.patch("utils.openai_client.get_openai_client", return_value=None)
    models = get_available_models_for_endpoint(
        "Personalizzato", endpoint_url="http://endpoint", api_key="key"
    )
    assert models[0] == "(Errore creazione client API)"
    assert DEFAULT_MODEL in models


def test_get_available_models_filters_embeddings(mocker):
    mock_get_client = mocker.patch("utils.openai_client.get_openai_client")
    dummy_models = [
        SimpleNamespace(id="gpt-4o"),
        SimpleNamespace(id="text-embedding-3-small"),
        SimpleNamespace(id="chat-model"),
        SimpleNamespace(id="my-embedding-model"),
    ]

    dummy_client = SimpleNamespace(models=SimpleNamespace(list=lambda: dummy_models))
    mock_get_client.return_value = dummy_client

    models = get_available_models_for_endpoint(
        "Personalizzato", endpoint_url="http://endpoint", api_key="key"
    )

    assert "text-embedding-3-small" not in models
    assert "my-embedding-model" not in models
    assert "gpt-4o" in models and "chat-model" in models
