from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ChicMatrix"
    database_url: str = "postgresql://chicmatrix:chicmatrix@db:5432/chicmatrix"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://frontend:3000"

    # Auth / email verification
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@chicmatrix.app"
    verification_token_expire_hours: int = 24
    frontend_url: str = "http://localhost:3002"
    api_base_url: str = "http://localhost:8001"
    consent_version: str = "1.0"
    email_debug: bool = True

    # Phone / OTP
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    otp_expire_minutes: int = 10
    sms_debug: bool = True

    # Social login
    google_client_id: str = ""
    google_client_secret: str = ""
    apple_client_id: str = ""
    apple_team_id: str = ""
    apple_key_id: str = ""
    apple_private_key: str = ""
    social_auth_debug: bool = True

    # JWT / sessions
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
