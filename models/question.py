from dataclasses import dataclass
from typing import Optional
import uuid
import pandas as pd
from sqlalchemy import text

from models.db_utils import get_engine

@dataclass
class Question:
    id: str
    domanda: str
    risposta_attesa: str
    categoria: str = ""

    @staticmethod
    def load_all() -> pd.DataFrame:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM questions", engine)
        if 'categoria' not in df.columns:
            df['categoria'] = ""
        df['id'] = df['id'].astype(str)
        df['domanda'] = df['domanda'].astype(str).fillna("")
        df['risposta_attesa'] = df['risposta_attesa'].astype(str).fillna("")
        df['categoria'] = df['categoria'].astype(str).fillna("")
        return df

    @staticmethod
    def add(domanda: str, risposta_attesa: str, categoria: str = "", question_id: Optional[str] = None) -> str:
        qid = question_id or str(uuid.uuid4())
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO questions (id, domanda, risposta_attesa, categoria) VALUES (:id, :domanda, :risposta_attesa, :categoria)"
                ),
                {"id": qid, "domanda": domanda, "risposta_attesa": risposta_attesa, "categoria": categoria},
            )
        return qid

    @staticmethod
    def update(question_id: str, domanda: Optional[str] = None, risposta_attesa: Optional[str] = None, categoria: Optional[str] = None) -> None:
        updates = []
        params = {"id": question_id}
        if domanda is not None:
            updates.append("domanda=:domanda")
            params["domanda"] = domanda
        if risposta_attesa is not None:
            updates.append("risposta_attesa=:risposta_attesa")
            params["risposta_attesa"] = risposta_attesa
        if categoria is not None:
            updates.append("categoria=:categoria")
            params["categoria"] = categoria
        if not updates:
            return
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text(f"UPDATE questions SET {', '.join(updates)} WHERE id=:id"), params)

    @staticmethod
    def delete(question_id: str) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM question_set_questions WHERE question_id=:id"), {"id": question_id})
            conn.execute(text("DELETE FROM questions WHERE id=:id"), {"id": question_id})
