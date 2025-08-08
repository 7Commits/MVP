import logging

from dataclasses import dataclass, field
from typing import List, Optional
import uuid
from sqlalchemy import select

from models.database import DatabaseEngine
from models.orm_models import QuestionSetORM, QuestionORM
logger = logging.getLogger(__name__)


@dataclass
class QuestionSet:
    id: str
    name: str
    questions: List[str] = field(default_factory=list)

    @staticmethod
    def load_all() -> List["QuestionSet"]:
        with DatabaseEngine.instance().get_session() as session:
            sets = session.execute(select(QuestionSetORM)).scalars().all()
            return [
                QuestionSet(
                    id=s.id,
                    name=s.name or "",
                    questions=[q.id for q in s.questions],
                )
                for s in sets
            ]

    @staticmethod
    def create(name: str, question_ids: Optional[List[str]] = None) -> str:
        set_id = str(uuid.uuid4())
        q_ids = [str(q) for q in (question_ids or [])]
        with DatabaseEngine.instance().get_session() as session:
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
        with DatabaseEngine.instance().get_session() as session:
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
        with DatabaseEngine.instance().get_session() as session:
            qset = session.get(QuestionSetORM, set_id)
            if qset:
                session.delete(qset)
            session.commit()
