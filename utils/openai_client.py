"""Utility per interagire con le API dei provider LLM."""

import logging
from typing import Any, List

from openai import OpenAI

logger = logging.getLogger(__name__)

DEFAULT_MODEL: str = "gpt-4o"
DEFAULT_ENDPOINT: str = "https://api.openai.com/v1"


class ClientCreationError(Exception):
    """Eccezione sollevata quando la creazione del client OpenAI fallisce."""


def get_openai_client(api_key: str, base_url: str | None = None) -> OpenAI:
    """Crea e restituisce un client OpenAI configurato.

    Solleva ``ClientCreationError`` se la chiave API è mancante o la creazione fallisce.
    """

    if not api_key:
        logger.warning("Tentativo di creare client OpenAI senza chiave API.")
        raise ClientCreationError("Chiave API mancante")
    try:
        effective_base_url = (
            base_url
            if base_url and base_url.strip() and base_url != "custom"
            else DEFAULT_ENDPOINT
        )
        return OpenAI(api_key=api_key, base_url=effective_base_url)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Errore durante la creazione del client OpenAI: {exc}")
        raise ClientCreationError(str(exc)) from exc


def get_available_models_for_endpoint(
    provider_name: str,
    endpoint_url: str | None = None,
    api_key: str | None = None,
) -> List[str]:
    """Restituisce una lista di modelli disponibili basata sul provider o sull'endpoint."""
    # Aggiungi altri provider predefiniti qui
    # elif provider_name == "XAI":
    #     return XAI_MODELS
    if provider_name == "Personalizzato":
        if (
            not api_key
            or not endpoint_url
            or endpoint_url == "custom"
            or not endpoint_url.strip()
        ):
            return [
                "(Endpoint personalizzato non specificato)",
                DEFAULT_MODEL,
                "gpt-4",
                "gpt-3.5-turbo",
            ]

        try:
            client = get_openai_client(api_key=api_key, base_url=endpoint_url)
        except ClientCreationError:
            return ["(Errore creazione client API)", DEFAULT_MODEL]
        try:
            models_response: Any = client.models.list()
            models: Any = getattr(models_response, "data", models_response)
            filtered_models: List[str] = sorted(
                [
                    model.id
                    for model in models
                    if not any(
                        term in model.id.lower() for term in ["embed", "embedding"]
                    )
                    and (
                        any(
                            term in model.id.lower()
                            for term in ["chat", "instruct", "gpt", "claude", "grok"]
                        )
                        or len(model.id.split("-")) > 2
                    )
                ]
            )
            if not filtered_models:
                filtered_models = sorted(
                    [
                        model.id
                        for model in models
                        if not any(
                            term in model.id.lower() for term in ["embed", "embedding"]
                        )
                    ]
                )
            return filtered_models if filtered_models else [DEFAULT_MODEL]
        except Exception:
            return ["(Errore recupero modelli)", DEFAULT_MODEL]
    return [DEFAULT_MODEL]


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_ENDPOINT",
    "ClientCreationError",
    "get_openai_client",
    "get_available_models_for_endpoint",
]
