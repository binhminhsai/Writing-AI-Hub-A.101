from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class QuestionRequest(BaseModel):
    topic: str = Field(..., description="Tên chủ đề hoặc nội dung topic chính")
    sheet_id: Optional[str] = Field(None, description="ID của Google Sheet (nếu dùng)")
    doc_id: Optional[str] = Field(None, description="ID của Google Docs (nếu có)")

class TopicRequest(BaseModel):
    topic: str
    band: str
    task_type: str = "TASK2"  # Default to Task 2

class QuestionResponse(BaseModel):
    status: str
    question: str
    outline: str
    vocabulary_suggestions: str
    sentence_suggestions: str
    topic: str
    band: str
    task_type: str
    error: Optional[str] = None
    details: Optional[str] = None
    traceback: Optional[str] = None
