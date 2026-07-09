from fastapi import APIRouter

from app.config import settings
from app.schemas.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", service=settings.app_name)
