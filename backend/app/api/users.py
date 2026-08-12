import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.models import User
from app.schemas.user import UserProfileUpdate, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(user: User = Depends(get_current_user)):
    return user


@router.patch("/me/profile", response_model=UserResponse)
def update_my_profile(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User profile updated", extra={"user_id": str(user.id)})
    return user
