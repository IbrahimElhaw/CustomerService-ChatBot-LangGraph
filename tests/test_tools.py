from langchain_core.messages import AIMessage

from support_bot.db import init_db
from support_bot.graph import build_graph
from support_bot.tools import get_order_status
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        from langchain_core.runnables import RunnableLambda

        return RunnableLambda(lambda _: schema(category="order"))


def test_order_status_tool_found():
    init_db()
    assert "shipped" in get_order_status.invoke({"order_id": "sn-1001"})


def test_order_status_tool_not_found():
    init_db()
    assert "Keine Bestellung" in get_order_status.invoke({"order_id": "SN-9999"})


def test_agent_calls_tool_then_answers():
    init_db()
    tool_call = AIMessage(
        content="",
        tool_calls=[{"name": "get_order_status", "args": {"order_id": "SN-1001"}, "id": "c1"}],
    )
    fake = FakeToolModel(messages=iter([tool_call, AIMessage("Ihre Bestellung ist unterwegs.")]))
    graph = build_graph(llm=fake)

    out = graph.invoke({"messages": [("user", "Wo ist SN-1001?")]}, {"configurable": {"thread_id": "t"}})

    assert out["messages"][-2].type == "tool"
    assert "shipped" in out["messages"][-2].content
    assert out["messages"][-1].content == "Ihre Bestellung ist unterwegs."