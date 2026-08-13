import enum


class SocialProvider(str, enum.Enum):
    GOOGLE = "google"
    APPLE = "apple"


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class StyleCode(str, enum.Enum):
    """Closed vocabulary v1 for product style tagging (multi-label)."""

    FORMAL = "formal"
    SPORT = "sport"
    BIKER = "biker"
    ROCKER = "rocker"
    CASUAL = "casual"
    MINIMAL = "minimal"
    STREETWEAR = "streetwear"


STYLE_TAG_CATALOG: list[dict[str, str]] = [
    {"code": StyleCode.FORMAL.value, "label_es": "Formales"},
    {"code": StyleCode.SPORT.value, "label_es": "Deporte"},
    {"code": StyleCode.BIKER.value, "label_es": "Motociclistas"},
    {"code": StyleCode.ROCKER.value, "label_es": "Rockeros"},
    {"code": StyleCode.CASUAL.value, "label_es": "Casual"},
    {"code": StyleCode.MINIMAL.value, "label_es": "Minimal"},
    {"code": StyleCode.STREETWEAR.value, "label_es": "Streetwear"},
]
