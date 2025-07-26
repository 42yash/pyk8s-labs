from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This tells Pydantic to look for environment variables in a .env file
    # which is useful for local development, though we use docker-compose.yml here.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database Configuration
    # The value will be read from the DATABASE_URL environment variable
    # defined in docker-compose.yml
    DATABASE_URL: str

    # A default value can be provided if the env var is not set.
    # We will add more variables here later (e.g., SECRET_KEY).
    PROJECT_NAME: str = "PyK8s-Lab"


# Create a single, reusable instance of the settings
settings = Settings()