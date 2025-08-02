"""Funzioni di utilità per gestire le domande e la relativa cache."""
import pandas as pd
from models.question import Question
from services.cache import (
    get_questions as _get_questions,
    refresh_questions as _refresh_questions,
)


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
    """Aggiunge una domanda solo se non esiste già.

    Parametri
    ----------
    question_id: str
        Identificatore della domanda da aggiungere.
    domanda: str
        Testo della domanda.
    risposta_attesa: str
        Risposta attesa.
    categoria: str, opzionale
        Categoria della domanda.

    Restituisce
    -------
    bool
        ``True`` se la domanda è stata aggiunta, ``False`` se esisteva già.
    """
    df = Question.load_all()
    if str(question_id) in df["id"].astype(str).values:
        return False

    Question.add(domanda, risposta_attesa, categoria, question_id)
    refresh_questions()
    return True
