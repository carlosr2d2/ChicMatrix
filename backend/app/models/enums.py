import enum


class SocialProvider(str, enum.Enum):
    GOOGLE = "google"
    APPLE = "apple"


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
