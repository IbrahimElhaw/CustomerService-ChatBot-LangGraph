import sys
from uuid import uuid4

from support_bot.checkpointer import get_checkpointer

from support_bot.graph import build_graph
from langgraph.types import Command

thread_id = sys.argv[1] if len(sys.argv) > 1 else uuid4().hex[:8]
config = {"configurable": {"thread_id": thread_id}}

with get_checkpointer() as checkpointer:
    graph = build_graph(checkpointer=checkpointer)
    print(f"Thread: {thread_id}  (fortsetzen: python scripts/chat_cli.py {thread_id})")

    state = graph.get_state(config)
    if state.values.get("messages"):
        print("Bot (letzte Nachricht):", state.values["messages"][-1].content)

    result = {"__interrupt__": state.tasks[0].interrupts} if state.next else {}
    while True:
        while "__interrupt__" in result:
            frage = result["__interrupt__"][0].value["frage"]
            antwort = input(f"[MITARBEITER] {frage} (y/n): ").strip().lower()
            decision = "approve" if antwort == "y" else "reject"
            result = graph.invoke(Command(resume=decision), config)
            print("Bot:", result["messages"][-1].content)

        text = input("Du: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        result = graph.invoke({"messages": [("user", text)]}, config)
        if "__interrupt__" not in result:
            print("Bot:", result["messages"][-1].content)