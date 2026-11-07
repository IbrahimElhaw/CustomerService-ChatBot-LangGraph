from langchain_core.tools import tool

from .db import get_conn


@tool
def get_order_status(order_id: str) -> str:
    """Gibt Status, Versanddienstleister und voraussichtliche Lieferung einer Bestellung zurück.
    order_id hat das Format SN-1234."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT status, carrier, estimated_arrival FROM orders WHERE order_id = ?",
            (order_id.strip().upper(),),).fetchone()
    if row is None:
        return f"Keine Bestellung mit der Nummer {order_id} gefunden."
    return (f"Status: {row['status']},"
            f" Versand: {row['carrier'] or 'noch nicht versendet'},"
            f" Lieferung: {row['estimated_arrival']}")


@tool
def get_tracking_info(order_id: str) -> str:
    """Gibt die Sendungsnummer einer Bestellung zurück, falls sie bereits versendet wurde."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT carrier, tracking_number FROM orders WHERE order_id = ?",
            (order_id.strip().upper(),),
        ).fetchone()
    if row is None:
        return f"Keine Bestellung mit der Nummer {order_id} gefunden."
    if not row["tracking_number"]:
        return "Die Bestellung wurde noch nicht versendet, daher gibt es keine Sendungsnummer."
    return f"{row['carrier']}-Sendungsnummer: {row['tracking_number']}"


ORDER_TOOLS = [get_order_status, get_tracking_info]