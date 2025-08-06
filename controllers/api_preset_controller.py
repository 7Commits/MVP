"""Utility per la gestione dei preset API."""

import logging

import uuid
from typing import List, Optional, Tuple

import pandas as pd

from models.api_preset import APIPreset
from utils.cache import (
    get_api_presets as _get_api_presets,
    refresh_api_presets as _refresh_api_presets,
)
from openai import APIConnectionError, APIStatusError, RateLimitError

from . import openai_client
logger = logging.getLogger(__name__)


def load_presets() -> pd.DataFrame:
    """Restituisce i preset API utilizzando la cache."""
    return _get_api_presets()


def refresh_api_presets() -> pd.DataFrame:
    """Svuota e ricarica la cache dei preset API."""
    return _refresh_api_presets()


def list_presets(df: pd.DataFrame | None = None) -> List[dict]:
    """Restituisce l'elenco dei preset come lista di dizionari."""
    if df is None:
        df = load_presets()
    return df.to_dict(orient="records")


def get_preset_by_id(
    preset_id: str, df: pd.DataFrame | None = None
) -> Optional[dict]:
    """Recupera un singolo preset dato il suo ID."""
    if df is None:
        df = load_presets()
    match = df[df["id"] == preset_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def validate_preset(data: dict, preset_id: Optional[str] = None) -> Tuple[bool, str]:
    """Valida i dati di un preset prima del salvataggio."""
    name = data.get("name", "").strip()
    if not name:
        return False, "Il nome del preset non può essere vuoto."

    df = load_presets()
    if preset_id:
        df = df[df["id"] != preset_id]
    if name in df["name"].values:
        return False, f"Un preset con nome '{name}' esiste già."
    return True, ""


def save_preset(
    data: dict, preset_id: Optional[str] = None
) -> Tuple[bool, str, pd.DataFrame]:
    """Salva un nuovo preset o aggiorna uno esistente."""
    is_valid, message = validate_preset(data, preset_id)
    if not is_valid:
        return False, message, load_presets()

    df = load_presets()
    preset_data = {
        "name": data.get("name"),
        "endpoint": data.get("endpoint"),
        "api_key": data.get("api_key"),
        "model": data.get("model"),
        "temperature": float(data.get("temperature", 0.0)),
        "max_tokens": int(data.get("max_tokens", 1000)),
    }

    if preset_id:
        idx = df.index[df["id"] == preset_id]
        if not idx.empty:
            for key, value in preset_data.items():
                df.loc[idx[0], key] = value
        success_message = f"Preset '{preset_data['name']}' aggiornato con successo!"
    else:
        preset_data["id"] = str(uuid.uuid4())
        df = pd.concat([df, pd.DataFrame([preset_data])], ignore_index=True)
        success_message = f"Preset '{preset_data['name']}' creato con successo!"

    APIPreset.save_df(df)
    updated_df = refresh_api_presets()
    return True, success_message, updated_df


def delete_preset(preset_id: str) -> Tuple[bool, str, pd.DataFrame]:
    """Elimina un preset e ritorna lo stato aggiornato."""
    df = load_presets()
    match = df[df["id"] == preset_id]
    if match.empty:
        return False, "Preset non trovato.", df

    preset_name = match.iloc[0]["name"]
    APIPreset.delete(preset_id)
    updated_df = refresh_api_presets()
    return True, f"Preset '{preset_name}' eliminato.", updated_df


def test_api_connection(
    api_key: str, endpoint: str, model: str, temperature: float, max_tokens: int
) -> Tuple[bool, str]:
    """Testa la connessione all'API LLM con i parametri forniti."""

    client = openai_client.get_openai_client(api_key=api_key, base_url=endpoint)
    if not client:
        return False, "Client API non inizializzato. Controlla chiave API e endpoint."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Test connessione. Rispondi solo con: 'Connessione riuscita.'",
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        if "Connessione riuscita." in content:
            return True, "Connessione API riuscita!"
        return (
            False,
            "Risposta inattesa dall'API (potrebbe indicare un problema con il modello o l'endpoint): "
            f"{content[:200]}...",
        )
    except APIConnectionError as e:
        return False, f"Errore di connessione API: {e}"
    except RateLimitError as e:
        return False, f"Errore di Rate Limit API: {e}"
    except APIStatusError as e:
        return (
            False,
            "Errore di stato API (es. modello '{model}' non valido per l'endpoint '{endpoint}', "
            f"autenticazione fallita, quota superata): {e.status_code} - {e.message}",
        )
    except Exception as exc:  # noqa: BLE001
        return False, (
            f"Errore imprevisto durante il test della connessione: {type(exc).__name__} - {exc}"
        )
