import re

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from ..db import get_conn
from ..state import SupportState

ORDER_ID_RE = re.compile(r"\bSN-\d{4}\b", re.IGNORECASE)

def returns_node(state: SupportState) -> dict:
    text = str(state["messages"][-1].content)

    match = ORDER_ID_RE.search(text)
    if not match:
        return {"messages": [AIMessage(
            "Gerne helfe ich bei der Retoure. Bitte nennen Sie mir Ihre Bestellnummer (Format SN-1234)."
        )]}

    order_id = match.group().upper()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT total_eur FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()
    if row is None:
        return {"messages": [AIMessage(f"Ich finde keine Bestellung mit der Nummer {order_id}.")]}

    decision = interrupt({
        "frage": f"Retoure für {order_id} über {row['total_eur']:.2f} € genehmigen?"
    })

    if decision == "approve":
        reply = f"Ihre Retoure für {order_id} wurde genehmigt."
    else:
        reply = f"Ihre Retoure für {order_id} wurde leider abgelehnt."
    return {"messages": [AIMessage(reply)]}