import re
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from support_bot.state import Route

HUMAN_RE = re.compile(r"\b(mensch|mitarbeiter|berater|beschwerde|anwalt)\b", re.IGNORECASE)

ROUTER_PROMPT = """Klassifiziere die Kundenanfrage in genau eine Kategorie:
- order: Status, Lieferung, Sendungsverfolgung einer Bestellung
- faq: allgemeine Fragen (Versandkosten, Zahlungsarten, Öffnungszeiten, AGB)
- returns: Rückgabe, Retoure, Erstattung, defekte Ware
- human: Kunde will mit einem Menschen sprechen oder ist sehr verärgert"""


class RouteDecision(BaseModel):
    category: Literal["order", "faq", "returns", "human"] = Field(description="Die passende Kategorie der Anfrage")


def rule_based_route(text: str) -> Literal["order", "faq", "returns", "human"] | None:
    if HUMAN_RE.search(text):
        return "human"
    return None


def classify(llm: BaseChatModel, text: str) -> Route:
    if rule_based_route(text) == "human":
        return "human"

    try:
        structured = llm.with_structured_output(RouteDecision)
        decision = structured.invoke([SystemMessage(ROUTER_PROMPT), HumanMessage(text)])
        return decision.category
    except Exception as e:
        print(e)
        return "faq"
