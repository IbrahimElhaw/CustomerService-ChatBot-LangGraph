import uuid

import psycopg
import pytest
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.postgres import PostgresSaver

from support_bot.config import settings
from support_bot.graph import build_graph

pytestmark = pytest.mark.integration


class FakeFaqModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        return RunnableLambda(lambda _: schema(category="faq"))


@pytest.fixture(scope="module")
def postgres_ok():
    try:
        psycopg.connect(settings.postgres_url, connect_timeout=2).close()
    except psycopg.OperationalError:
        pytest.skip("Postgres nicht erreichbar (docker compose up -d)")


def test_conversation_survives_restart(postgres_ok):
    doc = Document(page_content="Test", metadata={"source": "t.md"})
    cfg = {"configurable": {"thread_id": f"test-{uuid.uuid4().hex[:8]}"}}

    # "Sitzung 1"
    with PostgresSaver.from_conn_string(settings.postgres_url) as saver:
        saver.setup()
        fake = FakeFaqModel(messages=iter([AIMessage("Hallo Sam!")]))
        graph = build_graph(llm=fake, checkpointer=saver, retriever=lambda q: [doc])
        graph.invoke({"messages": [("user", "Hi, ich bin Sam")]}, cfg)

    # "Sitzung 2": neuer Saver, neuer Graph, gleicher thread_id
    with PostgresSaver.from_conn_string(settings.postgres_url) as saver:
        graph = build_graph(llm=FakeFaqModel(messages=iter([])), checkpointer=saver)
        messages = graph.get_state(cfg).values["messages"]

    assert any("Sam" in str(m.content) for m in messages)
    assert len(messages) == 2  # Nutzer + Bot
