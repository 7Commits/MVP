import os
import json
import uuid
from typing import Optional, Tuple, List

import pandas as pd

from models.question import Question
from services.question_service import load_questions, refresh_questions


def filter_questions_by_category(category: Optional[str] = None) -> Tuple[pd.DataFrame, List[str]]:
    """Ritorna le domande filtrate per categoria e la lista delle categorie disponibili."""
    df = load_questions()

    if df.empty:
        return df, []

    if "categoria" not in df.columns:
        df["categoria"] = ""
    else:
        df["categoria"] = df["categoria"].fillna("N/A")

    categories = sorted(list(df["categoria"].astype(str).unique()))

    if category:
        filtered_df = df[df["categoria"] == category]
    else:
        filtered_df = df

    return filtered_df, categories


def add_question(domanda: str, risposta_attesa: str, categoria: str = "", question_id: Optional[str] = None) -> str:
    qid = Question.add(domanda, risposta_attesa, categoria, question_id)
    refresh_questions()
    return qid


def update_question(
    question_id: str,
    domanda: Optional[str] = None,
    risposta_attesa: Optional[str] = None,
    categoria: Optional[str] = None,
) -> bool:
    """Aggiorna una domanda e restituisce l'esito dell'operazione."""
    updated = Question.update(question_id, domanda, risposta_attesa, categoria)
    refresh_questions()
    return updated


def delete_question(question_id: str) -> None:
    Question.delete(question_id)
    refresh_questions()


def import_questions_from_file(file) -> Tuple[bool, str]:
    """Importa domande da un file CSV o JSON."""
    try:
        file_extension = os.path.splitext(file.name)[1].lower()
        imported_df = None

        if file_extension == '.csv':
            imported_df = pd.read_csv(file)
        elif file_extension == '.json':
            data = json.load(file)
            if isinstance(data, list):
                imported_df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'questions' in data and isinstance(data['questions'], list):
                imported_df = pd.DataFrame(data['questions'])
            else:
                return False, "Il file JSON deve essere una lista di domande o contenere la chiave 'questions'."
        else:
            return False, "Formato file non supportato. Caricare un file CSV o JSON."

        if imported_df is None or imported_df.empty:
            return False, "Il file importato è vuoto o non contiene dati validi."

        if 'question' in imported_df.columns and 'domanda' not in imported_df.columns:
            imported_df.rename(columns={'question': 'domanda'}, inplace=True)
        if 'expected_answer' in imported_df.columns and 'risposta_attesa' not in imported_df.columns:
            imported_df.rename(columns={'expected_answer': 'risposta_attesa'}, inplace=True)

        required_columns = ['domanda', 'risposta_attesa']
        if not all(col in imported_df.columns for col in required_columns):
            return (
                False,
                f"Il file importato deve contenere le colonne '{required_columns[0]}' "
                f"e '{required_columns[1]}'.",
            )

        if 'id' not in imported_df.columns:
            imported_df['id'] = [str(uuid.uuid4()) for _ in range(len(imported_df))]
        else:
            imported_df['id'] = imported_df['id'].astype(str)

        if 'categoria' not in imported_df.columns:
            imported_df['categoria'] = ""
        else:
            imported_df['categoria'] = imported_df['categoria'].astype(str).fillna("")

        imported_df['domanda'] = imported_df['domanda'].astype(str).fillna("")
        imported_df['risposta_attesa'] = imported_df['risposta_attesa'].astype(str).fillna("")

        final_imported_df = imported_df[['id', 'domanda', 'risposta_attesa', 'categoria']]

        added_count = 0
        for _, row in final_imported_df.iterrows():
            Question.add(row['domanda'], row['risposta_attesa'], row['categoria'], question_id=row['id'])
            added_count += 1
        refresh_questions()
        return True, f"Importate con successo {added_count} domande."
    except Exception as e:
        return False, f"Errore durante l'importazione delle domande: {str(e)}"
