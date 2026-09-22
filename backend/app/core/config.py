from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./weather_ai.db"
    kma_api_key: str = ""
    kakao_rest_api_key: str = ""
    frontend_origin: str = "http://localhost:3000"


settings = Settings()
