import logging
from typing import List, Optional
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Application, Job, Candidate
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.repos.repos import ApplicationRepo, JobRepo, CandidateRepo
from app.repos.workflow_repos import HiringStageRepo, ApplicationStageTransitionRepo, CandidateScoreRepo

logger = logging.getLogger(__name__)


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.repo = ApplicationRepo(db)
        self.job_repo = JobRepo(db)
        self.candidate_repo = CandidateRepo(db)

    async def apply_for_job(
        self, 
        candidate_id: int, 
        application_in: ApplicationCreate,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Application:
        # 0. Idempotency Check
        existing_idempotent = await self.repo.get_by_idempotency_key(application_in.idempotency_key)
        if existing_idempotent:
            return existing_idempotent

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

        # 3. Application Limits
        candidate_apps = await self.repo.get_by_candidate(candidate_id)
        if len(candidate_apps) >= 10:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application limit reached"
            )

        # 4. Initialize Hiring Stage (Default: Applied)
        hiring_stage_repo = HiringStageRepo(self.db)
        default_stage = await hiring_stage_repo.get_default_stage()
        if not default_stage:
            # Fallback if no default stage exists in DB
            logger.warning("No default hiring stage found, creating application without stage")
            stage_id = None
        else:
            stage_id = default_stage.id

        # 5. Create Application
        application = await self.repo.create(obj_in={
            "candidate_id": candidate_id,
            "job_id": application_in.job_id,
            "idempotency_key": application_in.idempotency_key,
            "current_stage_id": stage_id
        })

        # 6. Initialize Stage Transition
        if stage_id:
            transition_repo = ApplicationStageTransitionRepo(self.db)
            await transition_repo.create(obj_in={
                "application_id": application.id,
                "from_stage_id": None,
                "to_stage_id": stage_id
            })

        # 7. Trigger Async Pipeline
        if background_tasks:
            background_tasks.add_task(self.trigger_async_pipeline, application.id)

        return application

    async def trigger_async_pipeline(self, application_id: int):
        """Orchestrates async scoring, analytics and notification tasks."""
        # Note: In a real system, we might use Celery/RabbitMQ here.
        # For this implementation, we use FastAPI BackgroundTasks for simplicity.
        
        # 1. Candidate Scoring
        await self.score_candidate(application_id)
        
        # 2. Analytics Update
        await self.update_analytics(application_id)
        
        # 3. Notification Dispatch
        await self.send_notification(application_id)

    async def score_candidate(self, application_id: int):
        # Placeholder for ML-based scoring logic
        score_repo = CandidateScoreRepo(self.db)
        await score_repo.create(obj_in={
            "application_id": application_id,
            "score_type": "skill-match",
            "score": 0.85, # Dummy score
            "metadata_json": {"version": "v1-baseline"}
        })
        await self.db.commit()

    async def update_analytics(self, application_id: int):
        # Placeholder for analytics updates
        logger.info(f"Updating analytics for application {application_id}")
        await self.db.flush()

    async def send_notification(self, application_id: int):
        # Placeholder for notification dispatch
        logger.info(f"Sending notification for application {application_id}")
        await self.db.flush()

    async def get_application(self, app_id: int) -> Optional[Application]:
        return await self.repo.get(app_id)

    async def update_status(self, app_id: int, app_update: ApplicationUpdate) -> Optional[Application]:
        db_app = await self.repo.get(app_id)
        if not db_app:
            return None
        return await self.repo.update(db_obj=db_app, obj_in=app_update.model_dump())
