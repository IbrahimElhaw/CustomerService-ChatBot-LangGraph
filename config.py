from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHOPNOW_")

    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:3b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.0

settings = Settings()