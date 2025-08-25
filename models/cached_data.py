import logging
from typing import List

from models.api_preset import APIPreset
from models.question import Question
from models.question_set import QuestionSet
from models.test_result import TestResult
logger = logging.getLogger(__name__)


def get_questions() -> List[Question]:
    return Question.load_all()


def get_question_sets() -> List[QuestionSet]:
    return QuestionSet.load_all()


def get_api_presets() -> List[APIPreset]:
    return APIPreset.load_all()


def get_results() -> List[TestResult]:
    return TestResult.load_all()
