from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, END
from support_bot.agents.router import classify
from support_bot.agents.order_agent import build_order_agent
from support_bot.agents.human_agent import human_handoff
from support_bot.agents.return_agent import returns_node

from .llm import get_llm
from .state import SupportState
from .agents.faq_agent import build_faq_node

def build_graph(llm=None, checkpointer=None, retriever=None):
    llm = (llm or get_llm())

    def router_node(state: SupportState) -> dict:
        last_user_text = state["messages"][-1].content
        return {"route": classify(llm, str(last_user_text))}

    builder = StateGraph(SupportState)
    builder.add_node("router", router_node)
    builder.add_node("order", build_order_agent(llm))
    builder.add_node("faq", build_faq_node(llm, retriever))
    builder.add_node("returns", returns_node)
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