from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, PipelineStage, JobStatus
from app.repos.pipeline_repos import JobSectionRepo, JobSkillRepo, JobKeywordRepo

class Stage6Persistence:
    stage_name = PipelineStage.PERSISTENCE
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def __call__(self, job: Job) -> None:
        """Stage 6: Persistence & Index Preparation"""
        # Data is already persisted in previous stages' transactional writes.
        # This stage could involve triggering external search index updates (ElasticSearch/Pinecone)
        # For now, we ensure DB data is consistent.
        pass

class Stage7Validation:
    stage_name = PipelineStage.VALIDATION
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.section_repo = JobSectionRepo(db)
        self.skill_repo = JobSkillRepo(db)
        self.kw_repo = JobKeywordRepo(db)

    async def __call__(self, job: Job) -> None:
        """Stage 7: Readiness Validation"""
        # Check if we have sections, skills, and keywords
        sections = await self.section_repo.get_by_job(job.id)
        skills = await self.skill_repo.get_by_job(job.id)
        keywords = await self.kw_repo.get_by_job(job.id)
        
        if not sections or not skills or not keywords:
            raise ValueError("Pipeline output validation failed: Missing structured data")
        
        # Integrity check: e.g., ensure "requirements" section exists
        if not any(s.section_type == "requirements" for s in sections):
            raise ValueError("Validation failed: Requirements section not found")
            
        # If all good, nothing to do here; orchestrator will mark job READY
