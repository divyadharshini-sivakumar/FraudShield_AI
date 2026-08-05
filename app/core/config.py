from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    FASTAPI_BASE_URL: str = "http://127.0.0.1:8000"

    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"
    OPENROUTER_API_KEY: str = ""

    DATABASE_URL: str = ""
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @property
    def get_database_url(self) -> str:
        if self.POSTGRES_PASSWORD:
            return (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/"
                f"{self.POSTGRES_DB}"
            )

        if self.DATABASE_URL:
            return self.DATABASE_URL

        return "sqlite:///./fraudshield.db"


settings = Settings()