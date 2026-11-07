from langchain_core.messages import AIMessage

from ..state import SupportState


def faq_stub(state: SupportState) -> dict:
    return {"messages": [AIMessage("[FAQ-Agent folgt] Dazu kann ich bald Auskunft geben.")]}


def returns_stub(state: SupportState) -> dict:
    return {"messages": [AIMessage("[Retouren-Agent folgt] Retouren sind bald hier möglich.")]}


def human_handoff(state: SupportState) -> dict:
    return {
        "messages": [
            AIMessage("Ich verbinde Sie mit einem Mitarbeiter. Bitte haben Sie einen Moment Geduld.")
        ]
    }