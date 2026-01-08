from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, PipelineStage, JobSection, JobSkill, JobKeyword
from app.repos.pipeline_repos import (
    JobNormalizedContentRepo, JobSectionRepo, 
    JobSkillRepo, JobKeywordRepo
)

class Stage3Classification:
    stage_name = PipelineStage.CLASSIFICATION
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.norm_repo = JobNormalizedContentRepo(db)
        self.section_repo = JobSectionRepo(db)

    async def __call__(self, job: Job) -> None:
        """Stage 3: Section Classification (Simplified regex-based)"""
        norm_content = await self.norm_repo.get_by_job(job.id)
        if not norm_content:
            raise ValueError("Normalized content missing for classification")
        
        text = norm_content.content
        
        # Simplified classification logic
        # In production, this would use NLP/LLM
        sections = self._classify_text(text)
        
        # Clear existing sections for idempotency (or update)
        existing = await self.section_repo.get_by_job(job.id)
        for s in existing:
            await self.section_repo.remove(id=s.id)
            
        for i, (s_type, content) in enumerate(sections.items()):
            await self.section_repo.create(obj_in={
                "job_id": job.id,
                "section_type": s_type,
                "content": content,
                "order": i
            })

    def _classify_text(self, text: str) -> Dict[str, str]:
        # Dummy logic: split by common headers or just chunks
        # This is a placeholder for a real classifier
        return {
            "requirements": "Extracted requirements placeholder",
            "responsibilities": "Extracted responsibilities placeholder",
            "benefits": "Extracted benefits placeholder"
        }

class Stage4SkillExtraction:
    stage_name = PipelineStage.SKILL_EXTRACTION
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.skill_repo = JobSkillRepo(db)

    async def __call__(self, job: Job) -> None:
        """Stage 4: Skill Extraction"""
        # Placeholder logic
        skills = [
            {"name": "Python", "type": "technical", "score": 0.9},
            {"name": "FastAPI", "type": "technical", "score": 0.85},
            {"name": "Teamwork", "type": "soft", "score": 0.7}
        ]
        
        existing = await self.skill_repo.get_by_job(job.id)
        for s in existing:
            await self.skill_repo.remove(id=s.id)
            
        for s in skills:
            await self.skill_repo.create(obj_in={
                "job_id": job.id,
                "skill_name": s["name"],
                "skill_type": s["type"],
                "score": s["score"]
            })

class Stage5KeywordExtraction:
    stage_name = PipelineStage.KEYWORD_EXTRACTION
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kw_repo = JobKeywordRepo(db)

    async def __call__(self, job: Job) -> None:
        """Stage 5: Keyword Extraction"""
        # Placeholder logic
        keywords = ["Backend", "Senior", "Remote", "Cloud"]
        
        existing = await self.kw_repo.get_by_job(job.id)
        for kw in existing:
            await self.kw_repo.remove(id=kw.id)
            
        for kw in keywords:
            await self.kw_repo.create(obj_in={
                "job_id": job.id,
                "keyword": kw,
                "weight": 1.0
            })
