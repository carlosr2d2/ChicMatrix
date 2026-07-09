from app.models.enums import UserRole

ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.USER.value: [
        "read:profile",
        "write:profile",
        "read:recommendations",
        "read:products",
    ],
    UserRole.ADMIN.value: [
        "read:profile",
        "write:profile",
        "read:recommendations",
        "read:products",
        "admin:users",
        "admin:retailers",
        "admin:scrape",
    ],
}


def permissions_for_role(role: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[UserRole.USER.value])
