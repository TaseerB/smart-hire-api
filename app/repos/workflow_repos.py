from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import HiringStage, ApplicationStageTransition, CandidateScore
from app.repos.base import BaseRepo


class HiringStageRepo(BaseRepo[HiringStage]):
    def __init__(self, db: AsyncSession):
        super().__init__(HiringStage, db)

    async def get_default_stage(self) -> Optional[HiringStage]:
        query = select(HiringStage).where(HiringStage.is_default == True).order_by(HiringStage.order)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[HiringStage]:
        query = select(HiringStage).where(HiringStage.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class ApplicationStageTransitionRepo(BaseRepo[ApplicationStageTransition]):
    def __init__(self, db: AsyncSession):
        super().__init__(ApplicationStageTransition, db)

    async def get_history_for_application(self, application_id: int) -> List[ApplicationStageTransition]:
        query = select(ApplicationStageTransition).where(
            ApplicationStageTransition.application_id == application_id
        ).order_by(ApplicationStageTransition.created_at)
        result = await self.db.execute(query)
        return result.scalars().all()


class CandidateScoreRepo(BaseRepo[CandidateScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(CandidateScore, db)

    async def get_scores_for_application(self, application_id: int) -> List[CandidateScore]:
        query = select(CandidateScore).where(
            CandidateScore.application_id == application_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()
