"""Utilità di supporto per interagire con l'API di OpenAI."""

# mypy: ignore-errors

import logging
from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"
DEFAULT_ENDPOINT = "https://api.openai.com/v1"

# Modelli disponibili per diversi provider (esempio)
OPENAI_MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
ANTHROPIC_MODELS = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]
# Aggiungi altri provider e modelli se necessario
# XAI_MODELS = ["grok-1"]


def get_openai_client(api_key: str, base_url: str = None):
    """
    Crea e restituisce un client OpenAI configurato.
    Parametri:
        api_key: La chiave API.
        base_url: L'URL base dell'endpoint API (opzionale, default a OpenAI).
    Restituisce:
        Un'istanza del client OpenAI o None se la chiave API non è fornita.
    """
    if not api_key:
        logging.warning("Tentativo di creare client OpenAI senza chiave API.")
        return None
    try:
        effective_base_url = (
            base_url if base_url and base_url.strip() and base_url != "custom" else DEFAULT_ENDPOINT
        )
        return OpenAI(api_key=api_key, base_url=effective_base_url)
    except Exception as exc:
        logging.error(f"Errore durante la creazione del client OpenAI: {exc}")
        return None


def get_available_models_for_endpoint(
    provider_name: str, endpoint_url: str = None, api_key: str = None
):
    """
    Restituisce una lista di modelli disponibili basata sul provider o tenta di elencarli dall'endpoint.
    Parametri:
        provider_name: Nome del provider (es. "OpenAI", "Anthropic", "Personalizzato").
        endpoint_url: URL dell'endpoint (rilevante per "Personalizzato").
        api_key: Chiave API per autenticarsi (necessaria per elencare modelli da endpoint personalizzati).
    Restituisce:
        Una lista di stringhe con i nomi dei modelli.
    """
    if provider_name == "OpenAI":
        return OPENAI_MODELS
    elif provider_name == "Anthropic":
        return ANTHROPIC_MODELS
    # Aggiungi altri provider predefiniti qui
    # elif provider_name == "XAI":
    #     return XAI_MODELS
    elif provider_name == "Personalizzato":
        if not api_key or not endpoint_url or endpoint_url == "custom" or not endpoint_url.strip():
            return ["(Endpoint personalizzato non specificato)", DEFAULT_MODEL, "gpt-4", "gpt-3.5-turbo"]

        client = get_openai_client(api_key=api_key, base_url=endpoint_url)
        if not client:
            return ["(Errore creazione client API)", DEFAULT_MODEL]
        try:
            models = client.models.list()
            filtered_models = sorted(
                [
                    model.id
                    for model in models
                    if not any(term in model.id.lower() for term in ["embed", "embedding"])
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
                    [model.id for model in models if not any(term in model.id.lower() for term in ["embed", "embedding"])]
                )
            return filtered_models if filtered_models else [DEFAULT_MODEL]
        except Exception:
            return ["(Errore recupero modelli)", DEFAULT_MODEL]
    return [DEFAULT_MODEL]
