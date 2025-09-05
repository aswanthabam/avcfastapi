from pydantic_settings import SettingsConfigDict

from ...settings import BaseSettings


class Config(BaseSettings):
    DEBUG: bool = False
    PHONEPE_CLIENT_ID: str
    PHONEPE_CLIENT_SECRET: str
    PHONEPE_PAYMENT_EXPIRY_SECONDS: int


settings = Config()
