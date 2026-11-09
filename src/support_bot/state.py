from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

Route = Literal["order", "faq", "returns", "human", "blocked", "ok"]


class SupportState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: Route
