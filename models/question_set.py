from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import pandas as pd
from sqlalchemy import select

from models.db_utils import get_session
from models.orm_models import QuestionSetORM, QuestionORM


@dataclass
class QuestionSet:
    id: str
    name: str
    questions: List[str] = field(default_factory=list)

    @staticmethod
    def load_all() -> pd.DataFrame:
        with get_session() as session:
            sets = session.execute(select(QuestionSetORM)).scalars().all()
            data = []
            for s in sets:
                data.append({
                    "id": s.id,
                    "name": s.name or "",
                    "questions": [q.id for q in s.questions],
                })
        columns = ["id", "name", "questions"]
        return pd.DataFrame(data, columns=columns)

    @staticmethod
    def create(name: str, question_ids: Optional[List[str]] = None) -> str:
        set_id = str(uuid.uuid4())
        q_ids = [str(q) for q in (question_ids or [])]
        with get_session() as session:
            qs = []
            for qid in q_ids:
                q_obj = session.get(QuestionORM, qid)
                if q_obj:
                    qs.append(q_obj)
            qset = QuestionSetORM(id=set_id, name=name, questions=qs)
            session.add(qset)
            session.commit()
        return set_id

    @staticmethod
    def update(set_id: str, name: Optional[str] = None, question_ids: Optional[List[str]] = None) -> None:
        with get_session() as session:
            qset = session.get(QuestionSetORM, set_id)
            if not qset:
                return
            if name is not None:
                qset.name = name
            if question_ids is not None:
                qs = []
                for qid in question_ids:
                    q_obj = session.get(QuestionORM, qid)
                    if q_obj:
                        qs.append(q_obj)
                qset.questions = qs
            session.commit()

    @staticmethod
    def delete(set_id: str) -> None:
        with get_session() as session:
            qset = session.get(QuestionSetORM, set_id)
            if qset:
                session.delete(qset)
            session.commit()
