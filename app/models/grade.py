# app/models/grade.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class GradeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class GradeEntry(BaseModel):
    student_id: str
    course_id: str
    teacher_id: str
    score: float
    max_score: float = 100.0
    assessment_type: str  # "quiz", "assignment", "midterm", "final"
    description: Optional[str] = None
    date: datetime = datetime.now()
    status: GradeStatus = GradeStatus.PENDING
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None

class FinalResult(BaseModel):
    student_id: str
    course_id: str
    semester: str
    total_score: float
    average: float
    grade: str            # A, B, C, D, F
    is_published: bool = False
    approved_by: Optional[str] = None