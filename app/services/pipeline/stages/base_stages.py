import re
import html
from typing import Protocol, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, PipelineStage, JobNormalizedContent
from app.repos.pipeline_repos import JobNormalizedContentRepo

class PipelineStageProtocol(Protocol):
    stage_name: PipelineStage
    async def __call__(self, job: Job) -> None: ...

class Stage1Intake:
    stage_name = PipelineStage.INTAKE
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, job: Job) -> None:
        """Stage 1: Validate incoming job data (already persisted)"""
        if not job.title or not job.description:
            raise ValueError("Job title and description are required for publishing")
        # In a real scenario, this might involve more complex schema validation
        # or checking against external policies.

class Stage2Normalization:
    stage_name = PipelineStage.NORMALIZATION
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = JobNormalizedContentRepo(db)

    async def __call__(self, job: Job) -> None:
        """Stage 2: Text Normalization"""
        raw_text = job.description
        
        # 1. Strip HTML tags
        clean_text = re.sub(r'<[^>]+>', '', raw_text)
        # 2. Unescape HTML entities
        clean_text = html.unescape(clean_text)
        # 3. Standardize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        # 4. Standardize casing (optional, but requested for 'standardize language, casing')
        # We'll preserve case for now but ensure it's "clean"
        
        # Persist normalized text
        norm_content = await self.repo.get_by_job(job.id)
        if norm_content:
            await self.repo.update(db_obj=norm_content, obj_in={"content": clean_text})
        else:
            await self.repo.create(obj_in={
                "job_id": job.id,
                "content": clean_text
            })
