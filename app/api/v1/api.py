from fastapi import APIRouter
from app.api.v1 import jobs, candidates, applications

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
