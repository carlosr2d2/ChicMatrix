from app.models.enums import UserRole
from app.permissions import ROLE_PERMISSIONS, permissions_for_role


def test_user_role_permissions():
    permissions = permissions_for_role(UserRole.USER.value)
    assert "read:profile" in permissions
    assert "read:recommendations" in permissions
    assert "admin:users" not in permissions


def test_admin_role_permissions():
    permissions = permissions_for_role(UserRole.ADMIN.value)
    assert "admin:users" in permissions
    assert "admin:retailers" in permissions


def test_unknown_role_falls_back_to_user_permissions():
    permissions = permissions_for_role("unknown-role")
    assert permissions == ROLE_PERMISSIONS[UserRole.USER.value]
