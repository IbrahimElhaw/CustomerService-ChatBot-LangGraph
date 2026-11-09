import httpx
import pytest

from support_bot.config import settings
from support_bot.rag import get_vectorstore, ingest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def ollama_ok():
    try:
        httpx.get(settings.ollama_base_url, timeout=2)
    except httpx.HTTPError:
        pytest.skip("Ollama nicht erreichbar")


def test_retrieval_finds_right_document(tmp_path, ollama_ok):
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "versand.md").write_text(
        "# Versand\n## Kosten\nDer Standardversand kostet 4,90 Euro. Ab 50 Euro Bestellwert ist der Versand kostenlos.\n",
        encoding="utf-8",
    )
    (kb / "retoure.md").write_text(
        "# Rückgabe\n## Frist\nSie können Artikel innerhalb von 30 Tagen nach Erhalt zurücksenden.\n",
        encoding="utf-8",
    )
    chroma = tmp_path / "chroma"

    ingest(knowledge_dir=kb, persist_dir=chroma)
    store = get_vectorstore(persist_dir=chroma)
    top = store.similarity_search("Wie viele Tage habe ich Zeit zum Zurücksenden?", k=1)[0]

    assert top.metadata["source"] == "retoure.md"
