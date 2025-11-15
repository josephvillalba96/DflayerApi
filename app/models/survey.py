"""
Survey Model (SURVEYS y SURVEY_RESPONSES)
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import sqlalchemy as sa
from app.models.base import Base


class QuestionType(str, enum.Enum):
    """Enum for question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    TRIVIA = "trivia"
    OPINION = "opinion"


class Survey(Base):
    """Survey model (SURVEYS)"""
    __tablename__ = "surveys"

    survey_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    question_text = Column(String(500), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    correct_answer = Column(Text, nullable=True)  # para trivia
    options = Column(Text, nullable=True)  # JSON array de opciones
    created_at = Column(Date, default=datetime.utcnow)
    expires_at = Column(Date, nullable=True)

    # Relationships
    post = relationship("Content", back_populates="surveys")
    responses = relationship("SurveyResponse", back_populates="survey")


class SurveyResponse(Base):
    """Survey response model (SURVEY_RESPONSES)"""
    __tablename__ = "survey_responses"

    response_id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.survey_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    responded_at = Column(Date, default=datetime.utcnow)

    # Relationships
    survey = relationship("Survey", back_populates="responses")
    user = relationship("User", back_populates="survey_responses")

    # Unique constraint: one response per user per survey
    __table_args__ = (
        sa.UniqueConstraint('survey_id', 'user_id', name='uq_survey_user'),
        {'sqlite_autoincrement': True},
    )

