from os import path
from pydantic import BaseSettings, Field

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    application_name: str = "pelleum-api"
    environment: str = "unknown"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_prefix: str = ""

    database_url: str = None

    user_login_name: str
    yodlee_base_url: str
    yodlee_client_id: str
    yodlee_secret: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
