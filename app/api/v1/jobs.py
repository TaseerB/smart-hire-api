from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.job import Job, JobCreate, JobUpdate
from app.services.job_service import JobService

router = APIRouter()


@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_in: JobCreate
) -> Any:
    service = JobService(db)
    return await service.create_job(job_in)


@router.get("/", response_model=List[Job])
async def read_jobs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    service = JobService(db)
    return await service.get_jobs(skip=skip, limit=limit)


@router.get("/{job_id}", response_model=Job)
async def read_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = JobService(db)
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks


@router.patch("/{job_id}", response_model=Job)
async def update_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    job_in: JobUpdate
) -> Any:
    service = JobService(db)
    job = await service.update_job(job_id, job_in)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = JobService(db)
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # We pass a new session to the background task if needed, but for now 
    # we'll use the service which can handle its own db lifecycle or share.
    # NOTE: In production, ensure the background task has its own session.
    background_tasks.add_task(service.publish_job, job_id)
    
    return {"message": "Job publishing pipeline started", "job_id": job_id}
