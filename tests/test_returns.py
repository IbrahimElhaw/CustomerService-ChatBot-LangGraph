from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.runnables import RunnableLambda
from langgraph.types import Command

from support_bot.db import init_db
from support_bot.graph import build_graph


class FakeReturnsModel(GenericFakeChatModel):
    """Fake-LLM: der Router bekommt immer 'returns', sonstige LLM-Aufrufe sind verboten."""

    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        return RunnableLambda(lambda _: schema(category="returns"))


def make_graph():
    init_db()
    # Leere Nachrichtenliste: würde ein Node das LLM wirklich aufrufen, schlägt der Test fehl
    return build_graph(llm=FakeReturnsModel(messages=iter([])))


def start_return(graph, cfg, text="Ich will SN-1003 zurückgeben"):
    return graph.invoke({"messages": [("user", text)]}, cfg)


def test_graph_pauses_before_decision():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r1"}}

    result = start_return(graph, cfg)

    assert "__interrupt__" in result
    assert "SN-1003" in result["__interrupt__"][0].value["frage"]
    assert graph.get_state(cfg).next == ("returns",)  # Graph steht still


def test_resume_approve():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r2"}}
    start_return(graph, cfg)

    out = graph.invoke(Command(resume="approve"), cfg)

    assert "genehmigt" in out["messages"][-1].content
    assert graph.get_state(cfg).next == ()  # Graph ist fertig


def test_resume_reject():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r3"}}
    start_return(graph, cfg)

    out = graph.invoke(Command(resume="reject"), cfg)

    assert "abgelehnt" in out["messages"][-1].content


def test_anything_but_approve_means_reject():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r4"}}
    start_return(graph, cfg)

    out = graph.invoke(Command(resume="vielleicht"), cfg)

    assert "abgelehnt" in out["messages"][-1].content


def test_unknown_order_does_not_interrupt():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r5"}}

    result = start_return(graph, cfg, "Ich will SN-9999 zurückgeben")

    assert "__interrupt__" not in result
    assert "keine Bestellung" in result["messages"][-1].content


def test_missing_order_number_asks_for_it():
    graph = make_graph()
    cfg = {"configurable": {"thread_id": "r6"}}

    result = start_return(graph, cfg, "Ich möchte etwas zurückgeben")

    assert "__interrupt__" not in result
    assert "Bestellnummer" in result["messages"][-1].content