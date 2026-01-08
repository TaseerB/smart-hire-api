import logging
import traceback
from datetime import datetime
from typing import List, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, JobStatus, PipelineStage, StageStatus, JobPipelineStep
from app.repos.repos import JobRepo
from app.repos.pipeline_repos import JobPipelineStepRepo

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepo(db)
        self.step_repo = JobPipelineStepRepo(db)

    async def run_pipeline(self, job_id: int, stages: List[Callable[[Job], Awaitable[None]]]):
        """
        Orchestrates the execution of pipeline stages.
        Ensures locking, state transitions, and failure handling.
        """
        job = await self.job_repo.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for pipeline execution")
            return

        # Acquire lock and transition to PROCESSING
        if not await self._acquire_lock(job):
            logger.warning(f"Job {job_id} is already being processed or failed to lock")
            return

        try:
            for stage_func in stages:
                stage_name = self._get_stage_name(stage_func)
                if not await self._run_stage(job, stage_name, stage_func):
                    # Stop pipeline if a stage fails
                    await self.job_repo.update(db_obj=job, obj_in={"status": JobStatus.FAILED})
                    return

            # Final validation and transition to READY
            await self.job_repo.update(db_obj=job, obj_in={
                "status": JobStatus.READY,
                "locked_at": None
            })
            logger.info(f"Job {job_id} successfully processed and marked READY")

        except Exception as e:
            logger.exception(f"Unexpected error in pipeline for job {job_id}: {str(e)}")
            await self.job_repo.update(db_obj=job, obj_in={
                "status": JobStatus.FAILED,
                "locked_at": None
            })
        finally:
            # Ensure lock is released if we finished or crashed
            if job.locked_at:
                await self.job_repo.update(db_obj=job, obj_in={"locked_at": None})
            await self.db.commit()

    async def _acquire_lock(self, job: Job) -> bool:
        """Acquires a logical lock for the job."""
        if job.locked_at and (datetime.utcnow() - job.locked_at).total_seconds() < 3600:
            # Lock is still valid (less than 1 hour old)
            return False

        await self.job_repo.update(db_obj=job, obj_in={
            "status": JobStatus.PROCESSING,
            "locked_at": datetime.utcnow()
        })
        await self.db.flush()
        return True

    async def _run_stage(self, job: Job, stage: PipelineStage, stage_func: Callable[[Job], Awaitable[None]]) -> bool:
        """Runs a single stage with state tracking and idempotency."""
        step = await self.step_repo.get_by_job_and_stage(job.id, stage)
        
        if step and step.status == StageStatus.COMPLETED:
            logger.info(f"Stage {stage} already completed for job {job.id}, skipping.")
            return True

        if not step:
            step = await self.step_repo.create(obj_in={
                "job_id": job.id,
                "stage": stage,
                "status": StageStatus.IN_PROGRESS,
                "started_at": datetime.utcnow()
            })
        else:
            await self.step_repo.update(db_obj=step, obj_in={
                "status": StageStatus.IN_PROGRESS,
                "error_message": None,
                "started_at": datetime.utcnow()
            })

        await self.db.flush()

        try:
            await stage_func(job)
            await self.step_repo.update(db_obj=step, obj_in={
                "status": StageStatus.COMPLETED,
                "completed_at": datetime.utcnow()
            })
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error in stage {stage} for job {job.id}: {str(e)}")
            await self.step_repo.update(db_obj=step, obj_in={
                "status": StageStatus.FAILED,
                "error_message": str(e),
                "metadata_json": {"traceback": traceback.format_exc()}
            })
            await self.db.flush()
            return False

    def _get_stage_name(self, func: Callable) -> PipelineStage:
        """Helper to map function to PipelineStage enum."""
        # This assumes the function name or a property maps to the enum
        # In a real implementation, stages might be classes or have explicit names
        return getattr(func, "stage_name", None)
