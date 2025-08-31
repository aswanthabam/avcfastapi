from avcfastapi.core.settings import BaseSettings


class MongoSettings(BaseSettings):
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
