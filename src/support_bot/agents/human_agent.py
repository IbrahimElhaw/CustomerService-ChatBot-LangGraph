from langchain_core.messages import AIMessage

from ..state import SupportState


def human_handoff(state: SupportState) -> dict:
    return {"messages": [AIMessage("Ich verbinde Sie mit einem Mitarbeiter. Bitte haben Sie einen Moment Geduld.")]}
