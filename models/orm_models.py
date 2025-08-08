"""Modelli ORM SQLAlchemy per i dati dell'applicazione."""

# mypy: ignore-errors

import logging

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship

from .database import Base
logger = logging.getLogger(__name__)

# Tabella di associazione per la relazione molti-a-molti tra set e domande
question_set_questions = Table(
    "question_set_questions",
    Base.metadata,
    Column("set_id", String(36), ForeignKey("question_sets.id"), primary_key=True),
    Column("question_id", String(36), ForeignKey("questions.id"), primary_key=True),
)


class QuestionORM(Base):
    __tablename__ = "questions"
    id = Column(String(36), primary_key=True)
    domanda = Column(Text, nullable=False)
    risposta_attesa = Column(Text, nullable=False)
    categoria = Column(Text, default="")

    sets = relationship(
        "QuestionSetORM", secondary=question_set_questions, back_populates="questions"
    )


class QuestionSetORM(Base):
    __tablename__ = "question_sets"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    questions = relationship(
        "QuestionORM", secondary=question_set_questions, back_populates="sets"
    )


class TestResultORM(Base):
    __tablename__ = "test_results"
    id = Column(String(36), primary_key=True)
    set_id = Column(String(36))
    timestamp = Column(Text)
    results = Column(JSON)


class APIPresetORM(Base):
    __tablename__ = "api_presets"
    id = Column(String(36), primary_key=True)
    name = Column(Text)
    provider_name = Column(Text)
    endpoint = Column(Text)
    api_key = Column(Text)
    model = Column(Text)
    temperature = Column(Float)
    max_tokens = Column(Integer)
