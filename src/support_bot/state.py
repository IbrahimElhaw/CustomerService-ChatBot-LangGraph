from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict


Route = Literal["order", "faq", "returns", "human"]

class SupportState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: Route