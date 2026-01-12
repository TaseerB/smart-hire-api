from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.models import ApplicationStatus


class ApplicationBase(BaseModel):
    job_id: int
    status: ApplicationStatus = ApplicationStatus.PENDING


class ApplicationCreate(BaseModel):
    job_id: int
    idempotency_key: str


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationInDBBase(ApplicationBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Application(ApplicationInDBBase):
    pass
