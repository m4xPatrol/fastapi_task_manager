from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DB_TEST_HOST: str
    DB_TEST_PORT: str
    DB_TEST_USER: str
    DB_TEST_PASSWORD: str
    DB_TEST_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=r".env"
    )  # check working directory in Run/Debug Configuration

    DB_URL: str = ""
    DB_TEST_URL: str = ""


settings = Settings()
settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
settings.DB_TEST_URL = f"postgresql+asyncpg://{settings.DB_TEST_USER}:{settings.DB_TEST_PASSWORD}@{settings.DB_TEST_HOST}:{settings.DB_TEST_PORT}/{settings.DB_TEST_NAME}"
