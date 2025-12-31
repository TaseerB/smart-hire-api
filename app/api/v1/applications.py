from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.application import Application, ApplicationCreate, ApplicationUpdate
from app.services.application_service import ApplicationService

router = APIRouter()


@router.post("/{candidate_id}/apply", response_model=Application, status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    candidate_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    application_in: ApplicationCreate
) -> Any:
    service = ApplicationService(db)
    return await service.apply_for_job(candidate_id, application_in)


@router.get("/{application_id}", response_model=Application)
async def read_application(
    application_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ApplicationService(db)
    application = await service.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{application_id}/status", response_model=Application)
async def update_application_status(
    application_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    application_update: ApplicationUpdate
) -> Any:
    service = ApplicationService(db)
    application = await service.update_status(application_id, application_update)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
