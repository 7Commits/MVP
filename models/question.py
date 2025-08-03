from dataclasses import dataclass
from typing import List, Optional
import uuid
from sqlalchemy import select, delete

from models.db_utils import get_session
from models.orm_models import QuestionORM, question_set_questions


@dataclass
class Question:
    id: str
    domanda: str
    risposta_attesa: str
    categoria: str = ""

    @staticmethod
    def load_all() -> List["Question"]:
        with get_session() as session:
            results = session.execute(select(QuestionORM)).scalars().all()
            return [
                Question(
                    id=q.id,
                    domanda=q.domanda or "",
                    risposta_attesa=q.risposta_attesa or "",
                    categoria=q.categoria or "",
                )
                for q in results
            ]

    @staticmethod
    def add(domanda: str, risposta_attesa: str, categoria: str = "", question_id: Optional[str] = None) -> str:
        qid = question_id or str(uuid.uuid4())
        with get_session() as session:
            session.add(
                QuestionORM(
                    id=qid,
                    domanda=domanda,
                    risposta_attesa=risposta_attesa,
                    categoria=categoria,
                )
            )
            session.commit()
        return qid

    @staticmethod
    def update(
        question_id: str,
        domanda: Optional[str] = None,
        risposta_attesa: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> bool:
        """Aggiorna una domanda esistente.

        Restituisce ``True`` se l'aggiornamento è andato a buon fine,
        ``False`` se la domanda non esiste.
        """
        with get_session() as session:
            q = session.get(QuestionORM, question_id)
            if not q:
                return False
            if domanda is not None:
                q.domanda = domanda
            if risposta_attesa is not None:
                q.risposta_attesa = risposta_attesa
            if categoria is not None:
                q.categoria = categoria
            session.commit()
            return True

    @staticmethod
    def delete(question_id: str) -> None:
        with get_session() as session:
            session.execute(
                delete(question_set_questions).where(question_set_questions.c.question_id == question_id)
            )
            q = session.get(QuestionORM, question_id)
            if q:
                session.delete(q)
            session.commit()
