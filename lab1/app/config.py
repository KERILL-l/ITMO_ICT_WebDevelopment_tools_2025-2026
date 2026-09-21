from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/timemanager"
    secret_key: str = "changeme-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    
    parser_url: str = "http://parser:8001"

    class Config:
        env_file = ".env"


settings = Settings()
