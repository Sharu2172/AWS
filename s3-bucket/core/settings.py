from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    access_key: str = Field(alias="AccessKey")
    secret_key: str = Field(alias="SecretKey")
    region: str = Field(alias="Region")
    bucket_name: str = Field(alias="BucketName")
