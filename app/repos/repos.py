from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, Candidate, Application
from app.repos.base import BaseRepo


class JobRepo(BaseRepo[Job]):
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)


class CandidateRepo(BaseRepo[Candidate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Candidate, db)

    async def get_by_email(self, email: str) -> Optional[Candidate]:
        query = select(Candidate).where(Candidate.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class ApplicationRepo(BaseRepo[Application]):
    def __init__(self, db: AsyncSession):
        super().__init__(Application, db)

    async def get_by_candidate_and_job(self, candidate_id: int, job_id: int) -> Optional[Application]:
        query = select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_id == job_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_candidate(self, candidate_id: int) -> List[Application]:
        query = select(Application).where(Application.candidate_id == candidate_id)
        result = await self.db.execute(query)
        return result.scalars().all()
