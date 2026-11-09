from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from support_bot.agents.guardrails import REFUSAL, check_input, check_output
from support_bot.agents.human_agent import human_handoff
from support_bot.agents.order_agent import build_order_agent
from support_bot.agents.return_agent import returns_node
from support_bot.agents.router import classify

from .agents.faq_agent import build_faq_node
from .llm import get_llm
from .state import SupportState


def build_graph(llm=None, checkpointer=None, retriever=None):
    llm = llm or get_llm()

    def router_node(state: SupportState) -> dict:
        last_user_text = state["messages"][-1].content
        return {"route": classify(llm, str(last_user_text))}

    builder = StateGraph(SupportState)
    builder.add_node("guard_input", guard_input)
    builder.add_node("router", router_node)
    builder.add_node("order", build_order_agent(llm))
    builder.add_node("faq", build_faq_node(llm, retriever))
    builder.add_node("returns", returns_node)
    builder.add_node("human", human_handoff)
    builder.add_node("guard_output", guard_output)

    builder.add_edge(START, "guard_input")
    builder.add_conditional_edges(
        "guard_input",
        lambda state: "blocked" if state.get("route") == "blocked" else "ok",
        {"blocked": END, "ok": "router"},
    )

    builder.add_conditional_edges("router", lambda state: state["route"], {"order": "order", "faq": "faq", "returns": "returns", "human": "human"})

    for node in ("order", "faq", "returns", "human"):
        builder.add_edge(node, "guard_output")
        builder.add_edge("guard_output", END)

    return builder.compile(checkpointer=checkpointer or MemorySaver())


def guard_input(state: SupportState) -> dict:
    text = str(state["messages"][-1].content)
    if check_input(text):
        # No problem
        return {"route": "ok"}
    return {"messages": [AIMessage(REFUSAL)], "route": "blocked"}


def guard_output(state: SupportState) -> dict:
    last = state["messages"][-1]
    replacement = check_output(str(last.content))
    if replacement is None:
        return {}
    # discard the last message and print refusal
    return {"messages": [AIMessage(replacement, id=last.id)]}
