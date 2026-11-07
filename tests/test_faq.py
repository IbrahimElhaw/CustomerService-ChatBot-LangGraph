from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from support_bot.agents.faq_agent import build_faq_node
from support_bot.prompts import NO_INFO_MESSAGE
from support_bot.rag import load_chunks

DOC = Document(page_content="Versand kostet 4,90 Euro.", metadata={"source": "versand.md"})


def test_load_chunks_splits_by_header_and_keeps_source(tmp_path):
    (tmp_path / "test.md").write_text(
        "# Titel\n## Eins\nText eins.\n## Zwei\nText zwei.\n", encoding="utf-8"
    )
    chunks = load_chunks(tmp_path)
    assert len(chunks) >= 2
    assert all(c.metadata["source"] == "test.md" for c in chunks)


def test_faq_node_answers_with_sources():
    llm = GenericFakeChatModel(messages=iter([AIMessage("Der Versand kostet 4,90 Euro.")]))
    node = build_faq_node(llm, retriever=lambda q: [DOC])

    out = node({"messages": [HumanMessage("Was kostet der Versand?")]})

    text = out["messages"][0].content
    assert "4,90" in text
    assert "Quellen: versand.md" in text


def test_faq_node_without_documents_does_not_call_llm():
    llm = GenericFakeChatModel(messages=iter([]))  # Aufruf würde einen Fehler auslösen
    node = build_faq_node(llm, retriever=lambda q: [])

    out = node({"messages": [HumanMessage("Irgendwas?")]})

    assert out["messages"][0].content == NO_INFO_MESSAGE