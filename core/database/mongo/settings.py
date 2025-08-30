from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="APP_")

    DATABASE_URL: str
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


settings = MongoSettings()
