from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import date as dt_date
from enum import Enum

# --- Common Models ---

class StandardResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None

# --- Auth Models ---

class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1, description="Environment-stored password")

# --- Journal Models ---

class ActionItem(BaseModel):
    priority: Literal["P1", "P2", "P3", "P4", "P5"]
    status: Literal["Aktif"] = "Aktif"
    title: str = Field(..., description="Task name in Turkish")
    date: dt_date

class QuickJournalRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Raw journal entry content")
    title: Optional[str] = Field(None, max_length=200, description="Optional title, defaults to timestamp")

class FullJournalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    raw_content: str = Field(..., min_length=1)
    date: Optional[dt_date] = Field(None, description="Date in ISO format (YYYY-MM-DD)")
    emotions_detected: Optional[List[str]] = Field(None, max_length=10)
    key_insights: Optional[str] = None
    action_items: Optional[List[ActionItem]] = Field(None, description="Actionable tasks derived from journal")

# --- Review Models ---

ReviewType = Literal['weekly', 'monthly', 'quarterly', 'yearly']

class PeriodAssessment(str, Enum):
    SUCCESSFUL = "Başarılı"
    MIXED = "Karışık"
    CHALLENGING = "Zorlayıcı"

class GoalStatus(str, Enum):
    NOT_STARTED = "Başlamadı"
    IN_PROGRESS = "Devam Ediyor"
    COMPLETED = "Tamamlandı"
    POSTPONED = "Ertelendi"

class GoalUpdate(BaseModel):
    goal_name: str = Field(..., min_length=1, description="Exact name of the goal from context")
    new_status: GoalStatus
    progress_delta: int = Field(
        ...,
        ge=-100,
        le=100,
        description="Change in progress for this period. Can be negative if regressed."
    )
    notes: str = Field(..., min_length=1, description="Brief reasoning for change")

class SaveReviewRequest(BaseModel):
    review_type: ReviewType
    date: dt_date = Field(..., description="Review date YYYY-MM-DD")
    period_assessment: PeriodAssessment = Field(..., description="Overall assessment of the period")
    review_summary: str = Field(..., min_length=50)
    wins: List[str] = Field(..., min_length=1, max_length=50)
    challenges: List[str] = Field(..., min_length=1, max_length=50)
    lessons_learned: str = Field(..., min_length=1, description="Key takeaway from this period for future use.")
    goal_updates: List[GoalUpdate] = Field(default_factory=list)
    next_period_focus: List[str] = Field(..., min_length=1, max_length=20)
    
    @field_validator('review_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ['weekly', 'monthly', 'quarterly', 'yearly']:
            raise ValueError(f"Invalid review type: {v}")
        return v
