from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    hiring_stages: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    hiring_stages: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class JobInDBBase(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Job(JobInDBBase):
    pass
