from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class CandidateBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., max_length=255)
    profile_data: Dict[str, Any] = Field(default_factory=dict)


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None


class CandidateInDBBase(CandidateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Candidate(CandidateInDBBase):
    pass
