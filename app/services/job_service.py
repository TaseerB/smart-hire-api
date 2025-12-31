from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job
from app.schemas.job import JobCreate, JobUpdate
from app.repos.repos import JobRepo


class JobService:
    def __init__(self, db: AsyncSession):
        self.repo = JobRepo(db)

    async def create_job(self, job_in: JobCreate) -> Job:
        return await self.repo.create(obj_in=job_in.model_dump())

    async def get_job(self, job_id: int) -> Optional[Job]:
        return await self.repo.get(job_id)

    async def get_jobs(self, skip: int = 0, limit: int = 100) -> List[Job]:
        return await self.repo.get_multi(skip=skip, limit=limit)

    async def update_job(self, job_id: int, job_in: JobUpdate) -> Optional[Job]:
        db_job = await self.repo.get(job_id)
        if not db_job:
            return None
        return await self.repo.update(db_obj=db_job, obj_in=job_in.model_dump(exclude_unset=True))
