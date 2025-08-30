from pydantic_settings import BaseSettings, SettingsConfigDict


class SqlalchameySettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="APP_")

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    @property
    def cors_origins(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [
                origin.strip()
                for origin in self.CORS_ORIGINS.split(",")
                if origin.strip()
            ]
        return self.CORS_ORIGINS


settings = SqlalchameySettings()
