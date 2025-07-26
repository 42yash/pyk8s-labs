# backend/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    PROJECT_NAME: str = "PyK8s-Lab"

    # Add these new security settings
    # Replace the placeholder with the key you generated
    SECRET_KEY: str = "d76ed749832ebf841cb682c2c490386305ec6a0fb1e8bac515c8c8e32098d2b4"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Tokens will be valid for 30 minutes

    ENCRYPTION_KEY: str = "PbY-1_8HuIT8HyufhjJggOq_nj2FAY3dqlp7g8GWj88="


settings = Settings()