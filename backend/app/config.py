from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ChicMatrix"
    database_url: str = "postgresql://chicmatrix:chicmatrix@db:5432/chicmatrix"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://frontend:3000"

    class Config:
        env_file = ".env"


settings = Settings()
