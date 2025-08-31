from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="APP_")


class CoreSettings(BaseSettings):
    NAME: str
    SECRET_KEY: str
    DEBUG: bool = False
    CORS_ORIGINS: list[str] | str

    @property
    def cors_origins(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [
                origin.strip()
                for origin in self.CORS_ORIGINS.split(",")
                if origin.strip()
            ]
        return self.CORS_ORIGINS


settings = CoreSettings()
