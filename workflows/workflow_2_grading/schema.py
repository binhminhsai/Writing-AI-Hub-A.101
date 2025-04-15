from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union


class GradingRequest(BaseModel):
    """Request model for IELTS essay grading"""
    essay: str = Field(..., description="The student's essay text")
    question: str = Field(..., description="The IELTS question prompt")
    types: str = Field(..., description="The type of IELTS Writing Task 2 question")


class ScoreDetail(BaseModel):
    """Model for detailed criteria scores"""
    task: float = Field(..., alias="Task Response")
    coherence: float = Field(..., alias="Coherence and Cohesion")
    lexical: float = Field(..., alias="Lexical Resource")
    grammar: float = Field(..., alias="Grammatical Range and Accuracy")


class SentenceExplanation(BaseModel):
    """Base model for sentence explanations"""
    sentence: str


class GoodSentence(SentenceExplanation):
    """Model for good sentences"""
    reason: str


class WrongSentence(SentenceExplanation):
    """Model for wrong/incorrect sentences"""
    error: str
    correction: str
    reason: str


class ImprovableSentence(SentenceExplanation):
    """Model for improvable sentences"""
    issue: str
    improved: str
    reason: str


class HighlightCategories(BaseModel):
    """Model for sentence highlight categories"""
    green: List[str] = []
    red: List[str] = []
    yellow: List[str] = []


class Explanations(BaseModel):
    """Model for all sentence explanations"""
    green: List[GoodSentence] = []
    red: List[WrongSentence] = []
    yellow: List[ImprovableSentence] = []


class GradingResponse(BaseModel):
    """Response model for IELTS essay grading"""
    feedback: Dict[str, Any] = Field(..., description="Detailed feedback for each criterion")
    scores: ScoreDetail = Field(..., description="Scores for each criterion")
    average_band: float = Field(..., description="Overall IELTS band score (0.0-9.0)")
    essay_highlights: str = Field(..., description="HTML-formatted essay with highlighting")
    highlighted_sentences: HighlightCategories = Field(..., description="Sentences categorized by quality")
    explanations: Explanations = Field(..., description="Detailed explanations for highlighted sentences") 