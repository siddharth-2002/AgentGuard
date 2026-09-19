from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AgentGuard"
    environment: str = "development"
    database_url: str = "sqlite:///./data/agentguard.db"
    api_key: str = "change-me-in-production"
    moss_project_id: str = ""
    moss_project_key: str = ""
    request_timeout_seconds: float = 5.0
    max_request_chars: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
