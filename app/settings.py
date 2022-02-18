from os import path

from pydantic import BaseSettings

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "pelleum-api"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

    # Database Settings
    db_url: str

    # Auth Settings
    token_url: str
    json_web_token_secret: str
    json_web_token_algorithm: str
    access_token_expire_minutes: float

    # External Connection Settings
    account_connections_base_url: str

    # Pelleum-product-specific Settings
    max_rationale_limit: int = 25

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
