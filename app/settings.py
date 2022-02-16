from os import path

from pydantic import BaseSettings

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    application_name: str = "pelleum-api"
    environment: str = "unknown"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int = 8624
    server_prefix: str = ""

    db_username: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    db_engine: str

    token_url: str
    json_web_token_secret: str
    json_web_token_algorithm: str
    access_token_expire_minutes: float
    max_rationale_limit: int = 25

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()