from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import (
    JobPipelineStep, JobNormalizedContent, JobSection, 
    JobSkill, JobKeyword, PipelineStage
)
from app.repos.base import BaseRepo


class JobPipelineStepRepo(BaseRepo[JobPipelineStep]):
    def __init__(self, db: AsyncSession):
        super().__init__(JobPipelineStep, db)

    async def get_by_job_and_stage(self, job_id: int, stage: PipelineStage) -> Optional[JobPipelineStep]:
        query = select(JobPipelineStep).where(
            JobPipelineStep.job_id == job_id,
            JobPipelineStep.stage == stage
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_for_job(self, job_id: int) -> List[JobPipelineStep]:
        query = select(JobPipelineStep).where(JobPipelineStep.job_id == job_id).order_by(JobPipelineStep.id)
        result = await self.db.execute(query)
        return result.scalars().all()


class JobNormalizedContentRepo(BaseRepo[JobNormalizedContent]):
    def __init__(self, db: AsyncSession):
        super().__init__(JobNormalizedContent, db)

    async def get_by_job(self, job_id: int) -> Optional[JobNormalizedContent]:
        query = select(JobNormalizedContent).where(JobNormalizedContent.job_id == job_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class JobSectionRepo(BaseRepo[JobSection]):
    def __init__(self, db: AsyncSession):
        super().__init__(JobSection, db)

    async def get_by_job(self, job_id: int) -> List[JobSection]:
        query = select(JobSection).where(JobSection.job_id == job_id).order_by(JobSection.order)
        result = await self.db.execute(query)
        return result.scalars().all()


class JobSkillRepo(BaseRepo[JobSkill]):
    def __init__(self, db: AsyncSession):
        super().__init__(JobSkill, db)

    async def get_by_job(self, job_id: int) -> List[JobSkill]:
        query = select(JobSkill).where(JobSkill.job_id == job_id)
        result = await self.db.execute(query)
        return result.scalars().all()


class JobKeywordRepo(BaseRepo[JobKeyword]):
    def __init__(self, db: AsyncSession):
        super().__init__(JobKeyword, db)

    async def get_by_job(self, job_id: int) -> List[JobKeyword]:
        query = select(JobKeyword).where(JobKeyword.job_id == job_id)
        result = await self.db.execute(query)
        return result.scalars().all()
