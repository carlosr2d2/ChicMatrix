import pytest

from tests.e2e.conftest import post_json, post_json_raw


@pytest.mark.e2e
@pytest.mark.playwright
def test_email_register_verify_login_refresh_logout(api_request):
    register = post_json(
        api_request,
        "/register/email",
        {
            "email": "e2e@chicmatrix.app",
            "password": "SecurePass123",
            "name": "E2E User",
            "consent_accepted": True,
        },
    )
    assert register["verified"] is False
    token = register["verification_token"]
    assert token

    verify = post_json(api_request, "/verify/email", {"token": token})
    assert verify["verified"] is True

    login = post_json(
        api_request,
        "/login",
        {
            "method": "email",
            "email": "e2e@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    assert login["access_token"]
    assert login["refresh_token"]
    assert login["role"] == "user"
    assert "read:recommendations" in login["permissions"]

    me_response = api_request.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert me_response.ok
    me = me_response.json()
    assert me["email"] == "e2e@chicmatrix.app"
    assert me["verified"] is True

    refreshed = post_json(
        api_request,
        "/login/refresh",
        {"refresh_token": login["refresh_token"]},
    )
    assert refreshed["access_token"]
    assert refreshed["refresh_token"] != login["refresh_token"]

    logout = post_json_raw(
        api_request,
        "/login/logout",
        {"refresh_token": refreshed["refresh_token"]},
    )
    assert logout.status == 204

    expired = post_json_raw(
        api_request,
        "/login/refresh",
        {"refresh_token": refreshed["refresh_token"]},
    )
    assert expired.status == 401


@pytest.mark.e2e
@pytest.mark.playwright
def test_phone_register_verify_login(api_request):
    register = post_json(
        api_request,
        "/register/phone",
        {
            "phone": "+573009991122",
            "name": "Phone E2E",
            "consent_accepted": True,
        },
    )
    otp = register["otp_code"]
    assert otp

    verify = post_json(
        api_request,
        "/verify/phone",
        {"phone": "+573009991122", "otp_code": otp},
    )
    assert verify["verified"] is True

    otp_step = post_json_raw(
        api_request,
        "/login",
        {"method": "phone", "phone": "+573009991122"},
    )
    assert otp_step.ok
    login_otp = otp_step.json()["otp_code"]
    assert login_otp

    login = post_json(
        api_request,
        "/login",
        {
            "method": "phone",
            "phone": "+573009991122",
            "otp_code": login_otp,
        },
    )
    assert login["access_token"]
    assert login["refresh_token"]


@pytest.mark.e2e
@pytest.mark.playwright
def test_social_register_then_login(api_request):
    social_register = post_json(
        api_request,
        "/auth/social",
        {
            "provider": "google",
            "id_token": "debug-google:e2e-google-001:e2e.social@chicmatrix.app:E2E Social",
            "consent_accepted": True,
        },
    )
    assert social_register["verified"] is True

    login = post_json(
        api_request,
        "/login",
        {
            "method": "social",
            "provider": "google",
            "id_token": "debug-google:e2e-google-001:e2e.social@chicmatrix.app:E2E Social",
        },
    )
    assert login["access_token"]
    assert login["user_id"] == social_register["user_id"]


@pytest.mark.e2e
@pytest.mark.playwright
def test_login_rejects_unknown_social_account(api_request):
    response = post_json_raw(
        api_request,
        "/login",
        {
            "method": "social",
            "provider": "google",
            "id_token": "debug-google:unknown-999:unknown@chicmatrix.app",
        },
    )
    assert response.status == 401
