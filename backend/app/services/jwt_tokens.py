import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Session as UserSession
from app.models.models import User
from app.permissions import permissions_for_role

logger = logging.getLogger(__name__)


class TokenError(Exception):
    pass


class JwtTokenService:
    def __init__(self, db: Session):
        self.db = db

    def create_access_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "permissions": permissions_for_role(user.role),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise TokenError("Invalid or expired access token") from exc

        if payload.get("type") != "access":
            raise TokenError("Invalid token type")
        return payload

    def create_refresh_session(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, UserSession]:
        raw_token = secrets.token_urlsafe(48)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return raw_token, session

    def validate_refresh_token(self, raw_token: str) -> UserSession:
        token_hash = self._hash_token(raw_token)
        session = (
            self.db.query(UserSession)
            .filter(UserSession.refresh_token_hash == token_hash)
            .first()
        )
        if not session:
            raise TokenError("Invalid refresh token")
        if session.revoked_at is not None:
            raise TokenError("Refresh token revoked")
        if self._as_utc(session.expires_at) < datetime.now(timezone.utc):
            raise TokenError("Refresh token expired")
        return session

    def revoke_session(self, session: UserSession) -> None:
        session.revoked_at = datetime.now(timezone.utc)
        self.db.commit()

    def rotate_refresh_token(
        self,
        raw_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str, User]:
        session = self.validate_refresh_token(raw_token)
        user = self.db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise TokenError("User not found")

        self.revoke_session(session)
        access_token = self.create_access_token(user)
        new_refresh_token, _ = self.create_refresh_session(
            user, user_agent=user_agent, ip_address=ip_address
        )
        return access_token, new_refresh_token, user

    def issue_token_pair(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        access_token = self.create_access_token(user)
        refresh_token, _ = self.create_refresh_session(
            user, user_agent=user_agent, ip_address=ip_address
        )
        return access_token, refresh_token

    def get_user_from_access_token(self, token: str) -> User:
        payload = self.decode_access_token(token)
        try:
            user_id = UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise TokenError("Invalid token subject") from exc

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise TokenError("User not found")
        return user

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
