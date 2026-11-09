from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHOPNOW_")

    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:3b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.0

    embedding_model: str = "nomic-embed-text"
    knowledge_dir: Path = PROJECT_ROOT / "company_documents"
    chroma_dir: Path = PROJECT_ROOT / "chroma_db"
    retrieval_k: int = 4

    checkpointer_backend: str = "memory"
    postgres_url: str = "postgresql://support:support@localhost:5432/support_bot"
    data_dir: Path = PROJECT_ROOT / "data"


settings = Settings()
