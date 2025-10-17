from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MessageCreate(BaseModel):
    session_id: str
    content: str


class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    session_id: str


class SessionRead(BaseModel):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    escalated: bool
    faq_match_id: Optional[int] = None


class FAQCreate(BaseModel):
    question: str
    answer: str


class FAQRead(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    session_id: str
    summary: str


