from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.candidate import Candidate, CandidateCreate, CandidateUpdate
from app.services.candidate_service import CandidateService

router = APIRouter()


@router.post("/", response_model=Candidate, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    *,
    db: AsyncSession = Depends(get_db),
    candidate_in: CandidateCreate
) -> Any:
    service = CandidateService(db)
    return await service.create_candidate(candidate_in)


@router.get("/{candidate_id}", response_model=Candidate)
async def read_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = CandidateService(db)
    candidate = await service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}", response_model=Candidate)
async def update_candidate(
    *,
    db: AsyncSession = Depends(get_db),
    candidate_id: int,
    candidate_in: CandidateUpdate
) -> Any:
    service = CandidateService(db)
    candidate = await service.update_candidate(candidate_id, candidate_in)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
