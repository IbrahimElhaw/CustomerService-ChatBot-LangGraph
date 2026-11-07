from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from support_bot.graph import build_graph


class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        # Router bekommt immer "faq", ohne Nachrichten des Fake-LLM zu verbrauchen
        return RunnableLambda(lambda _: schema(category="faq"))


def test_thread_keeps_history():
    fake = FakeToolModel(messages=iter([AIMessage("Hallo!"), AIMessage("Gern!")]))
    doc = Document(page_content="Test", metadata={"source": "test.md"})
    graph = build_graph(llm=fake, retriever=lambda q: [doc])
    cfg = {"configurable": {"thread_id": "t1"}}

    graph.invoke({"messages": [("user", "Hi")]}, cfg)
    out = graph.invoke({"messages": [("user", "Danke")]}, cfg)

    assert len(out["messages"]) == 4  # 2x user + 2x bot
    assert "Gern!" in out["messages"][-1].content