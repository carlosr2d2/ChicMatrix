import logging

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.metrics import RECOMMENDATIONS
from app.models.models import User
from app.schemas.schemas import RecommendationResponse
from app.services.recommendation import RecommendationEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("/{user_id}", response_model=RecommendationResponse)
def get_recommendations(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    engine = RecommendationEngine(db)
    recommendations = engine.recommend(user, limit=12)

    RECOMMENDATIONS.labels(user_id=str(user_id)).inc()
    logger.info(
        "Recommendations generated",
        extra={"user_id": user_id, "count": len(recommendations)},
    )

    return RecommendationResponse(user_id=user_id, recommendations=recommendations)
