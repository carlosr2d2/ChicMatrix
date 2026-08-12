import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.metrics import RECOMMENDATIONS
from app.models.models import User
from app.schemas.schemas import RecommendationResponse
from app.services.recommendation import RecommendationEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommend", tags=["recommendations"])


def _build_recommendations(user: User, db: Session) -> RecommendationResponse:
    engine = RecommendationEngine(db)
    recommendations = engine.recommend(user, limit=12)

    RECOMMENDATIONS.labels(user_id=str(user.id)).inc()
    logger.info(
        "Recommendations generated",
        extra={"user_id": str(user.id), "count": len(recommendations)},
    )
    return RecommendationResponse(user_id=user.id, recommendations=recommendations)


@router.get("/me", response_model=RecommendationResponse)
def get_my_recommendations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _build_recommendations(user, db)


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _build_recommendations(user, db)
