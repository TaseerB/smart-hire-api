from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Application, Job, Candidate
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.repos.repos import ApplicationRepo, JobRepo, CandidateRepo


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.repo = ApplicationRepo(db)
        self.job_repo = JobRepo(db)
        self.candidate_repo = CandidateRepo(db)

    async def apply_for_job(self, candidate_id: int, application_in: ApplicationCreate) -> Application:
        # 1. Verification: Job exists and is active
        job = await self.job_repo.get(application_in.job_id)
        if not job or not job.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or is no longer active"
            )

        # 2. Duplicate Check: Candidate hasn't already applied for this job
        existing_app = await self.repo.get_by_candidate_and_job(candidate_id, application_in.job_id)
        if existing_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate already applied for this job"
            )

        # 3. Application Limits (Example: Max 5 active applications)
        # This is where more complex logic would go
        # For now, just a simple limit check
        candidate_apps = await self.repo.get_by_candidate(candidate_id)
        # Filter for active apps if needed
        if len(candidate_apps) >= 10: # Production limit example
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application limit reached"
            )

        # 4. Eligibility checks (Example: based on requirements)
        # In a real system, we'd compare candidate profile with job.requirements
        
        return await self.repo.create(obj_in={
            "candidate_id": candidate_id,
            "job_id": application_in.job_id
        })

    async def get_application(self, app_id: int) -> Optional[Application]:
        return await self.repo.get(app_id)

    async def update_status(self, app_id: int, app_update: ApplicationUpdate) -> Optional[Application]:
        db_app = await self.repo.get(app_id)
        if not db_app:
            return None
        return await self.repo.update(db_obj=db_app, obj_in=app_update.model_dump())
