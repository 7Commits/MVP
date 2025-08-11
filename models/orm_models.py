"""Modelli ORM SQLAlchemy per i dati dell'applicazione."""

import logging

from typing import List

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Table, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    domanda: Mapped[str] = mapped_column(Text, nullable=False)
    risposta_attesa: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(Text, default="")

    sets: Mapped[List["QuestionSetORM"]] = relationship(
        "QuestionSetORM", secondary=question_set_questions, back_populates="questions"
    )


class QuestionSetORM(Base):
    __tablename__ = "question_sets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    questions: Mapped[List["QuestionORM"]] = relationship(
        "QuestionORM", secondary=question_set_questions, back_populates="sets"
    )


class TestResultORM(Base):
    __tablename__ = "test_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    set_id: Mapped[str] = mapped_column(String(36))
    timestamp: Mapped[str] = mapped_column(Text)
    results: Mapped[dict] = mapped_column(JSON)


class APIPresetORM(Base):
    __tablename__ = "api_presets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    provider_name: Mapped[str] = mapped_column(Text)
    endpoint: Mapped[str] = mapped_column(Text)
    api_key: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(Text)
    temperature: Mapped[float] = mapped_column(Float)
    max_tokens: Mapped[int] = mapped_column(Integer)
