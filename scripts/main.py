from support_bot.graph import build_graph

graph = build_graph()
config = {"configurable": {"thread_id": "cli-1"}}

while True:
    text = input("Du: ").strip()
    if text.lower() in {"exit", "quit"}:
        break
    result = graph.invoke({"messages": [("user", text)]}, config)
    print("Bot:", result["messages"][-1].content)