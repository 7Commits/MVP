from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import pandas as pd
from sqlalchemy import text

from models.db_utils import get_engine

@dataclass
class QuestionSet:
    id: str
    name: str
    questions: List[str] = field(default_factory=list)

    @staticmethod
    def load_all() -> pd.DataFrame:
        engine = get_engine()
        sets_df = pd.read_sql("SELECT id, name FROM question_sets", engine)
        rel_df = pd.read_sql("SELECT set_id, question_id FROM question_set_questions", engine)
        sets_df['questions'] = sets_df['id'].apply(lambda sid: rel_df[rel_df['set_id']==sid]['question_id'].tolist())
        sets_df['id'] = sets_df['id'].astype(str)
        sets_df['name'] = sets_df['name'].astype(str).fillna("")
        return sets_df

    @staticmethod
    def create(name: str, question_ids: Optional[List[str]] = None) -> str:
        set_id = str(uuid.uuid4())
        q_ids = [str(q) for q in (question_ids or [])]
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO question_sets (id, name) VALUES (:id, :name)"), {"id": set_id, "name": name})
            for qid in q_ids:
                conn.execute(text("INSERT INTO question_set_questions (set_id, question_id) VALUES (:sid, :qid)"), {"sid": set_id, "qid": qid})
        return set_id

    @staticmethod
    def update(set_id: str, name: Optional[str] = None, question_ids: Optional[List[str]] = None) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            if name is not None:
                conn.execute(text("UPDATE question_sets SET name=:name WHERE id=:id"), {"id": set_id, "name": name})
            if question_ids is not None:
                existing = conn.execute(text("SELECT question_id FROM question_set_questions WHERE set_id=:sid"), {"sid": set_id}).fetchall()
                existing_ids = [r[0] for r in existing]
                new_ids = [str(q) for q in question_ids]
                for qid in set(existing_ids) - set(new_ids):
                    conn.execute(text("DELETE FROM question_set_questions WHERE set_id=:sid AND question_id=:qid"), {"sid": set_id, "qid": qid})
                for qid in set(new_ids) - set(existing_ids):
                    conn.execute(text("INSERT INTO question_set_questions (set_id, question_id) VALUES (:sid, :qid)"), {"sid": set_id, "qid": qid})

    @staticmethod
    def delete(set_id: str) -> None:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM question_set_questions WHERE set_id=:id"), {"id": set_id})
            conn.execute(text("DELETE FROM question_sets WHERE id=:id"), {"id": set_id})
