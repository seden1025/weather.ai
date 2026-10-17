from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./weather_ai.db"
    kma_api_key: str = ""
    kakao_rest_api_key: str = ""
    frontend_origin: str = "http://localhost:3000"

    # 로그인 토큰 서명 키. 운영에서는 길고 무작위인 값으로 꼭 지정 (비우면 재시작마다 로그인이 풀림)
    auth_secret: str = ""
    token_ttl_days: int = 30
    # 보상용 연락처 조회 API용 관리자 토큰. 비워두면 조회 API가 비활성화된다.
    admin_token: str = ""


settings = Settings()
