from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Project(BaseSettings):
    """
    Описание проекта.
    """

    title: str = "Work in wallet Service"
    description: str = "Сервис работы с кошельками пользователей."
    release_version: str = Field(..., alias="PROJECT__RELEASE_VERSION")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="allow"
    )


class Settings(BaseSettings):
    """
    Настройки проекта.
    """

    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    project: Project = Field(default_factory=Project)
    base_url: str = Field(default="http://0.0.0.0:8000")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="allow"
    )


settings = Settings()
