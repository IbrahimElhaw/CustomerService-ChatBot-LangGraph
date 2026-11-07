from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END
from support_bot.agents.router import classify
from support_bot.agents.order_agent import build_order_agent
from support_bot.agents.stubs import *

from .llm import get_llm
from .state import SupportState


def build_graph(
    llm: BaseChatModel | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
):
    llm = (llm or get_llm())

    def router_node(state: SupportState) -> dict:
        last_user_text = state["messages"][-1].content
        return {"route": classify(llm, str(last_user_text))}

    builder = StateGraph(SupportState)
    builder.add_node("router", router_node)
    builder.add_node("order", build_order_agent(llm))
    builder.add_node("faq", faq_stub)
    builder.add_node("returns", returns_stub)
    builder.add_node("human", human_handoff)


    builder.add_edge(START, "router")
    builder.add_conditional_edges("router",
                                  lambda state: state["route"],
                                  {
                                      "order": "order",
                                      "faq": "faq",
                                      "returns": "returns",
                                      "human": "human"
                                  })

    for node in ("order", "faq", "returns", "human"):
        builder.add_edge(node, END)
    return builder.compile(checkpointer=checkpointer or MemorySaver())