from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.graph import build_graph


def test_thread_keeps_history():
    fake = GenericFakeChatModel(messages=iter([AIMessage("Hallo!"), AIMessage("Gern!")]))
    graph = build_graph(llm=fake)
    cfg = {"configurable": {"thread_id": "t1"}}

    graph.invoke({"messages": [("user", "Hi")]}, cfg)
    out = graph.invoke({"messages": [("user", "Danke")]}, cfg)

    assert len(out["messages"]) == 4  # 2x user + 2x bot

test_thread_keeps_history()