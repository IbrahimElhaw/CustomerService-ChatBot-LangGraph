from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from .config import settings
from .llm import get_embeddings


def load_chunks(knowledge_dir: Path) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2")], strip_headers=False)
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    chunks: list[Document] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for section in header_splitter.split_text(text):
            section.metadata["source"] = path.name
            chunks.extend(size_splitter.split_documents([section]))
    return chunks


def get_vectorstore(embeddings: Embeddings | None = None, persist_dir: Path | None = None) -> Chroma:
    return Chroma(
        collection_name="faq",
        embedding_function=embeddings or get_embeddings(),
        persist_directory=str(persist_dir or settings.chroma_dir),
    )


def ingest(
    knowledge_dir: Path | None = None,
    persist_dir: Path | None = None,
    embeddings: Embeddings | None = None,
) -> int:
    chunks = load_chunks(knowledge_dir or settings.knowledge_dir)
    if not chunks:
        raise RuntimeError(f"no .md files found in knowledge dir: {settings.knowledge_dir}")
    store = get_vectorstore(embeddings, persist_dir)
    store.reset_collection()
    store.add_documents(chunks)
    return len(chunks)


@lru_cache(maxsize=1)
def _default_store() -> Chroma:
    return get_vectorstore()


def default_retriever(query: str) -> list[Document]:
    return _default_store().similarity_search(query, k=settings.retrieval_k)
