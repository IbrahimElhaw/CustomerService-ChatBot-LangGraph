import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from support_bot.api import create_app
from support_bot.config import settings
from support_bot.db import init_db
from support_bot.graph import build_graph

DOC = Document(page_content="Test", metadata={"source": "t.md"})


def fake_llm(category: str, replies=()):
    class FakeModel(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

        def with_structured_output(self, schema, **kwargs):
            return RunnableLambda(lambda _: schema(category=category))

    return FakeModel(messages=iter([AIMessage(r) for r in replies]))


def make_client(category, replies=()):
    init_db()
    graph = build_graph(llm=fake_llm(category, replies), retriever=lambda q: [DOC])
    return TestClient(create_app(graph))


def test_chat_returns_reply():
    with make_client("faq", ["Hallo!"]) as client:
        r = client.post("/chat", json={"thread_id": "a1", "message": "Hi"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "Hallo!" in r.json()["reply"]


@pytest.mark.parametrize(
    "body",
    [
        {"thread_id": "a2", "message": ""},
        {"thread_id": "a2", "message": "x" * 1001},
        {"thread_id": "../etc", "message": "Hi"},
    ],
)
def test_invalid_input_is_rejected(body):
    with make_client("faq") as client:
        assert client.post("/chat", json=body).status_code == 422


def test_return_flow_pending_then_review():
    with make_client("returns") as client:
        r = client.post("/chat", json={"thread_id": "a3", "message": "Ich will SN-1003 zurückgeben"})
        assert r.json()["status"] == "pending_review"
        assert r.json()["review"]["order_id"] == "SN-1003"

        # solange die Freigabe aussteht, ist der Thread gesperrt
        r = client.post("/chat", json={"thread_id": "a3", "message": "Hallo?"})
        assert r.status_code == 409

        r = client.post("/review", json={"thread_id": "a3", "approved": True})
        assert r.json()["status"] == "ok"
        assert "genehmigt" in r.json()["reply"]


def test_review_without_pending_return_is_409():
    with make_client("faq") as client:
        r = client.post("/review", json={"thread_id": "a4", "approved": True})
    assert r.status_code == 409


def test_health_with_memory_backend(monkeypatch):
    monkeypatch.setattr(settings, "checkpointer_backend", "memory")
    with make_client("faq") as client:
        assert client.get("/health").status_code == 200