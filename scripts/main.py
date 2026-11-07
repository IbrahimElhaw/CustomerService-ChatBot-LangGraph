from langgraph.types import Command

from support_bot.graph import build_graph

graph = build_graph()
config = {"configurable": {"thread_id": "cli-1"}}

while True:
    text = input("Du: ").strip()
    if text.lower() in {"exit", "quit"}:
        break

    result = graph.invoke({"messages": [("user", text)]}, config)
    while "__interrupt__" in result:
        frage = result["__interrupt__"][0].value["frage"]
        antwort = input(f"[MITARBEITER] {frage} (y/n): ").strip().lower()
        decision = "approve" if antwort == "y" else "reject"
        result = graph.invoke(Command(resume=decision), config)

    print("Bot:", result["messages"][-1].content)