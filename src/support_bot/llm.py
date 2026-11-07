from langchain_core.language_models.chat_models import BaseChatModel
from .config import settings
from langchain_ollama import ChatOllama
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings


def get_embeddings() -> Embeddings:
    return OllamaEmbeddings(
        model=settings.embedding_model, base_url=settings.ollama_base_url)


def get_llm() -> BaseChatModel:
    return ChatOllama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature,
    )
