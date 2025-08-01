from typing import Optional, Tuple
import pandas as pd
import os
import json
import uuid
from models.question import Question


def load_questions() -> pd.DataFrame:
    return Question.load_all()


def add_question(domanda: str, risposta_attesa: str, categoria: str = "", question_id: Optional[str] = None) -> str:
    return Question.add(domanda, risposta_attesa, categoria, question_id)


def update_question(question_id: str, domanda: Optional[str] = None, risposta_attesa: Optional[str] = None, categoria: Optional[str] = None) -> None:
    Question.update(question_id, domanda, risposta_attesa, categoria)


def delete_question(question_id: str) -> None:
    Question.delete(question_id)


def add_question_if_not_exists(question_id: str, domanda: str, risposta_attesa: str, categoria: str = "") -> bool:
    df = Question.load_all()
    if str(question_id) in df['id'].astype(str).values:
        return False
    Question.add(domanda, risposta_attesa, categoria, question_id)
    return True


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
            return False, f"Il file importato deve contenere le colonne '{required_columns[0]}' e '{required_columns[1]}'."

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

        return True, f"Importate con successo {added_count} domande."
    except Exception as e:
        return False, f"Errore durante l'importazione delle domande: {str(e)}"
