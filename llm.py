from langchain_core.language_models.chat_models import BaseChatModel
from config import settings
from langchain_ollama import ChatOllama


def get_llm() -> BaseChatModel:
    if settings.llm_provider == "ollama":
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
        )
    raise ValueError(f"Unbekannter Provider: {settings.llm_provider}")
