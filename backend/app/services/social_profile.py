from dataclasses import dataclass


@dataclass
class SocialProfile:
    provider: str
    social_id: str
    email: str | None = None
    name: str | None = None
    email_verified: bool = True
