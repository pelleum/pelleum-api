from os import path
from pydantic import BaseSettings

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    application_name: str = "pelleum-api"
    environment: str = "unknown"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_prefix: str = ""

    database_url: str

    token_url: str
    json_web_token_secret: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
