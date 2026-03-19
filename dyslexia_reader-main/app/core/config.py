from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "sk-4544ded25f744a0b8e275af2db927135")
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"

    app_name: str = "Dyslexia Reader Backend"
    app_env: str = "dev"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 120
    database_url: str = "sqlite:///./dyslexia_reader.db"
    redis_url: str = "redis://localhost:6379/0"

    storage_bucket: str = "dyslexia-reader"
    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"

    ocr_provider: str = "mock"
    ocr_api_key: str | None = None
    ocr_api_url: str | None = None

    tts_provider: str = "mock"
    tts_api_key: str | None = None
    tts_api_url: str | None = None

    admin_email: str = "admin@example.com"

    # ====== 有道词典 API（免费版用网页爬取，商业版用官方API） ======
    YOUDAO_APP_KEY: str = "79b1f588cbcdede0"
    YOUDAO_APP_SECRET: str = "oI7qMYHunhcjWoykTurVLQTUgFnXLyBW"

    SPACY_EN_MODEL: str = "en_core_web_sm"
    # ====== TTS 配置 ======
    TTS_VOICE_ZH: str = "zh-CN-XiaoxiaoNeural"
    TTS_VOICE_EN: str = "en-US-JennyNeural"
    TTS_OUTPUT_DIR: str = os.path.join("storage", "audio")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)





settings = Settings()
