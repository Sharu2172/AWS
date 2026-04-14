import os
from typing import Any
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env_file = BASE_DIR / f".env.{os.getenv('ENV', 'dev')}"

class AWSSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    profile: str | None = Field(default=None, alias="AWS_PROFILE")
    access_key: str | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    secret_key: str | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    region: str = Field(default="ap-south-1", alias="AWS_REGION")
    bucket_name: str | None = Field(default=None, alias="AWS_BUCKET_NAME")

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default="dev", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "no", "off"}:
                return False
            if normalized in {"debug", "dev", "development", "true", "1", "yes", "on"}:
                return True
        return value

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    aws: AWSSettings = Field(default_factory=AWSSettings)
    app: AppConfig = Field(default_factory=AppConfig)
