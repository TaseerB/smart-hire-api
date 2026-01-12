import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum as SQLEnum, JSON, UniqueConstraint, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    HIRED = "hired"


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PipelineStage(str, enum.Enum):
    INTAKE = "intake"
    NORMALIZATION = "normalization"
    CLASSIFICATION = "classification"
    SKILL_EXTRACTION = "skill_extraction"
    KEYWORD_EXTRACTION = "keyword_extraction"
    PERSISTENCE = "persistence"
    VALIDATION = "validation"


class StageStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    hiring_stages: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Pipeline specific fields
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.DRAFT, index=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications: Mapped[List["Application"]] = relationship(back_populates="job")
    pipeline_steps: Mapped[List["JobPipelineStep"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    sections: Mapped[List["JobSection"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    skills: Mapped[List["JobSkill"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    keywords: Mapped[List["JobKeyword"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    normalized_content: Mapped[Optional["JobNormalizedContent"]] = relationship(back_populates="job", cascade="all, delete-orphan", uselist=False)


class JobPipelineStep(Base):
    __tablename__ = "job_pipeline_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    stage: Mapped[PipelineStage] = mapped_column(SQLEnum(PipelineStage))
    status: Mapped[StageStatus] = mapped_column(SQLEnum(StageStatus), default=StageStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    job: Mapped["Job"] = relationship(back_populates="pipeline_steps")

    __table_args__ = (
        UniqueConstraint("job_id", "stage", name="uq_job_stage"),
    )


class JobNormalizedContent(Base):
    __tablename__ = "job_normalized_contents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    content: Mapped[str] = mapped_column(Text)
    
    job: Mapped["Job"] = relationship(back_populates="normalized_content")


class JobSection(Base):
    __tablename__ = "job_sections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    section_type: Mapped[str] = mapped_column(String(50)) # e.g., requirements, responsibilities
    content: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    source_offset: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    job: Mapped["Job"] = relationship(back_populates="sections")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    skill_name: Mapped[str] = mapped_column(String(100), index=True)
    skill_type: Mapped[str] = mapped_column(String(20)) # technical, soft
    score: Mapped[float] = mapped_column(Float, default=0.0)

    job: Mapped["Job"] = relationship(back_populates="skills")


class JobKeyword(Base):
    __tablename__ = "job_keywords"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    keyword: Mapped[str] = mapped_column(String(100), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    job: Mapped["Job"] = relationship(back_populates="keywords")


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    profile_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    applications: Mapped[List["Application"]] = relationship(back_populates="candidate")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    
    # Workflow specific fields
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    current_stage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hiring_stages.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate: Mapped["Candidate"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    current_stage: Mapped[Optional["HiringStage"]] = relationship()
    transitions: Mapped[List["ApplicationStageTransition"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    scores: Mapped[List["CandidateScore"]] = relationship(back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),
    )


class HiringStage(Base):
    __tablename__ = "hiring_stages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[bool] = mapped_column(default=False)


class ApplicationStageTransition(Base):
    __tablename__ = "application_stage_transitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    from_stage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hiring_stages.id"), nullable=True)
    to_stage_id: Mapped[int] = mapped_column(ForeignKey("hiring_stages.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["Application"] = relationship(back_populates="transitions")


class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    score_type: Mapped[str] = mapped_column(String(50)) # e.g., skill-match, relevance
    score: Mapped[float] = mapped_column(Float)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["Application"] = relationship(back_populates="scores")
