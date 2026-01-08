from app.services.pipeline.orchestrator import PipelineOrchestrator
from app.services.pipeline.stages.base_stages import Stage1Intake, Stage2Normalization
from app.services.pipeline.stages.extraction_stages import Stage3Classification, Stage4SkillExtraction, Stage5KeywordExtraction
from app.services.pipeline.stages.final_stages import Stage6Persistence, Stage7Validation


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
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

    async def publish_job(self, job_id: int):
        orchestrator = PipelineOrchestrator(self.db)
        stages = [
            Stage1Intake(self.db),
            Stage2Normalization(self.db),
            Stage3Classification(self.db),
            Stage4SkillExtraction(self.db),
            Stage5KeywordExtraction(self.db),
            Stage6Persistence(self.db),
            Stage7Validation(self.db)
        ]
        await orchestrator.run_pipeline(job_id, stages)
