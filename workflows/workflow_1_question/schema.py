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

# Request model for preparing materials
# Used when the user clicks "Start Writing"
class PrepareMaterialsRequest(BaseModel):
    question: str = Field(..., description="The generated IELTS Writing question")
    topic: str = Field(..., description="The topic for the question")
    band: str = Field(..., description="The target band score")
    task_type: str = Field("TASK2", description="The task type (TASK1 or TASK2)")
    time_limit: int = Field(30, description="Time limit in minutes")

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
