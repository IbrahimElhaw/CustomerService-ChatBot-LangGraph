from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ..prompts import SYSTEM_PROMPT
from ..state import SupportState
from ..tools import ORDER_TOOLS


def build_order_agent(llm: BaseChatModel):
    llm_with_tools = llm.bind_tools(ORDER_TOOLS)

    def agent_node(state: SupportState) -> dict:
        response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response]}

    builder = StateGraph(SupportState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(ORDER_TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()
