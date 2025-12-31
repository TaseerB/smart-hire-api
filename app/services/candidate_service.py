from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.repos.repos import CandidateRepo


class CandidateService:
    def __init__(self, db: AsyncSession):
        self.repo = CandidateRepo(db)

    async def create_candidate(self, candidate_in: CandidateCreate) -> Candidate:
        existing_candidate = await self.repo.get_by_email(candidate_in.email)
        if existing_candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A candidate with this email already exists"
            )
        return await self.repo.create(obj_in=candidate_in.model_dump())

    async def get_candidate(self, candidate_id: int) -> Optional[Candidate]:
        return await self.repo.get(candidate_id)

    async def get_candidate_by_email(self, email: str) -> Optional[Candidate]:
        return await self.repo.get_by_email(email)

    async def update_candidate(self, candidate_id: int, candidate_in: CandidateUpdate) -> Optional[Candidate]:
        db_candidate = await self.repo.get(candidate_id)
        if not db_candidate:
            return None
        return await self.repo.update(db_obj=db_candidate, obj_in=candidate_in.model_dump(exclude_unset=True))
