from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL_FOR_TEST: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    TESTING: bool = False

    model_config = SettingsConfigDict(env_file="app/core/.env")  # check working directory in Run/Debug Configuration


settings = Settings()
