"""Controller per la gestione delle domande senza layer di service."""

import logging
from typing import Optional, Tuple, List, Dict, Any

import pandas as pd

from models.question import Question
from utils.cache import (
    get_questions as _get_questions,
    refresh_questions as _refresh_questions,
)

logger = logging.getLogger(__name__)


def load_questions() -> pd.DataFrame:
    """Restituisce tutte le domande utilizzando la cache."""
    return _get_questions()


def refresh_questions() -> pd.DataFrame:
    """Svuota e ricarica la cache delle domande."""
    return _refresh_questions()


def add_question_if_not_exists(
    question_id: str,
    domanda: str,
    risposta_attesa: str,
    categoria: str = "",
) -> bool:
    """Aggiunge una domanda solo se non esiste già."""

    df = load_questions()
    if str(question_id) in df["id"].astype(str).values:
        return False

    Question.add(domanda, risposta_attesa, categoria, question_id)
    refresh_questions()
    return True


def add_question(
    domanda: str,
    risposta_attesa: str,
    categoria: str = "",
    question_id: Optional[str] = None,
) -> str:
    """Aggiunge una nuova domanda e aggiorna la cache."""
    qid = Question.add(domanda, risposta_attesa, categoria, question_id)
    refresh_questions()
    return qid


def update_question(
    question_id: str,
    domanda: Optional[str] = None,
    risposta_attesa: Optional[str] = None,
    categoria: Optional[str] = None,
) -> bool:
    """Aggiorna una domanda esistente e ricarica la cache."""
    updated = Question.update(question_id, domanda, risposta_attesa, categoria)
    refresh_questions()
    return updated


def delete_question(question_id: str) -> None:
    """Elimina una domanda e aggiorna la cache."""
    Question.delete(question_id)
    refresh_questions()


def get_filtered_questions(category: Optional[str] = None) -> Tuple[pd.DataFrame, List[str]]:
    """Restituisce il ``DataFrame`` filtrato e l'elenco delle categorie."""
    return Question.filter_by_category(category)


def save_question_action(
    question_id: str, edited_question: str, edited_answer: str, edited_category: str
) -> dict:
    """Aggiorna una domanda e restituisce un dizionario con l'esito.

    Restituisce
    -----------
    dict
        ``{"success": bool, "questions_df": DataFrame | None}``

    In caso di successo viene anche ricaricata la lista delle domande.
    Eventuali errori sollevati da ``update_question`` vengono propagati.
    """
    success = update_question(
        question_id,
        domanda=edited_question,
        risposta_attesa=edited_answer,
        categoria=edited_category,
    )
    questions = refresh_questions() if success else None
    return {"success": success, "questions_df": questions}


def delete_question_action(question_id: str) -> pd.DataFrame:
    """Elimina una domanda e restituisce il ``DataFrame`` aggiornato."""
    delete_question(question_id)
    questions = refresh_questions()
    return questions


def import_questions_action(uploaded_file) -> Dict[str, Any]:
    """Importa domande da file e restituisce i risultati dell'operazione.

    Parametri
    ---------
    uploaded_file: file-like
        Il file caricato dall'utente.

    Restituisce
    -----------
    dict
        ``{"questions_df": DataFrame, "imported_count": int, "warnings": list[str]}``
    """

    if uploaded_file is None:
        raise ValueError("Nessun file caricato.")

    result = Question.import_from_file(uploaded_file)
    if not result["success"]:
        message = "; ".join(result.get("warnings", []))
        raise ValueError(message)

    questions = refresh_questions()
    return {
        "questions_df": questions,
        "imported_count": result["imported_count"],
        "warnings": result.get("warnings", []),
    }


def get_question_text(question_id: str, questions_df: Optional[pd.DataFrame] = None) -> str:
    """Ritorna il testo della domanda dato il suo ID, ricaricando la cache se necessario."""
    df = questions_df if questions_df is not None else load_questions()
    if "domanda" not in df.columns:
        df = refresh_questions()
        if "domanda" not in df.columns:
            return f"ID Domanda: {question_id} (colonna 'domanda' mancante)"
    row = df[df["id"] == str(question_id)]
    if not row.empty:
        return row.iloc[0]["domanda"]
    return f"ID Domanda: {question_id} (non trovata)"


def get_question_category(
    question_id: str, questions_df: Optional[pd.DataFrame] = None
) -> str:
    """Ritorna la categoria della domanda dato il suo ID, ricaricando la cache se necessario."""
    df = questions_df if questions_df is not None else load_questions()
    if "categoria" not in df.columns:
        df = refresh_questions()
        if "categoria" not in df.columns:
            return f"ID Domanda: {question_id} (colonna 'categoria' mancante)"
    row = df[df["id"] == str(question_id)]
    if not row.empty:
        return row.iloc[0]["categoria"]
    return f"ID Domanda: {question_id} (non trovata)"
