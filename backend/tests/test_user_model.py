import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.enums import SocialProvider
from app.models.models import User


def test_user_defaults(db_session):
    user = User(email="new@chicmatrix.app", name="New User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)
    assert user.verified is False
    assert user.password_hash is None
    assert user.phone is None
    assert user.otp_secret is None
    assert user.social_provider is None
    assert user.created_at is not None


def test_user_email_unique(db_session):
    db_session.add(User(email="dup@chicmatrix.app", name="A"))
    db_session.commit()
    db_session.add(User(email="dup@chicmatrix.app", name="B"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_phone_unique(db_session):
    db_session.add(User(phone="+573001234567", name="Phone User"))
    db_session.commit()
    db_session.add(User(phone="+573001234567", name="Other"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_user_social_provider_enum(db_session):
    user = User(
        email="social@chicmatrix.app",
        social_provider=SocialProvider.GOOGLE.value,
        social_id="google-123",
        verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.social_provider_enum == SocialProvider.GOOGLE


def test_user_supports_hybrid_auth_fields(db_session):
    user = User(
        email="hybrid@chicmatrix.app",
        phone="+573009998877",
        password_hash="$2b$12$hashed",
        otp_secret="otp-secret-key",
        verified=True,
        consent_version="1.0",
        name="Hybrid User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "hybrid@chicmatrix.app"
    assert user.phone == "+573009998877"
    assert user.password_hash is not None
    assert user.otp_secret is not None
    assert user.verified is True
