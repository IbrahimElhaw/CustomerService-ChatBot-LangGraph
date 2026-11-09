from contextlib import asynccontextmanager
from typing import Literal

import psycopg
from fastapi import FastAPI, HTTPException, Request
from langgraph.types import Command
from pydantic import BaseModel, Field

from .checkpointer import get_checkpointer
from .config import settings
from .graph import build_graph

THREAD_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


class ChatRequest(BaseModel):
    thread_id: str = Field(pattern=THREAD_PATTERN)
    message: str = Field(min_length=1, max_length=1000)


class ReviewRequest(BaseModel):
    thread_id: str = Field(pattern=THREAD_PATTERN)
    approved: bool


class ChatResponse(BaseModel):
    status: Literal["ok", "pending_review"]
    reply: str | None = None
    review: dict | None = None  # Freigabe-Frage, wenn status == "pending_review "


def _to_response(result: dict) -> ChatResponse:
    if "__interrupt__" in result:
        return ChatResponse(status="pending_review", review=result["__interrupt__"][0].value)
    return ChatResponse(status="ok", reply=str(result["messages"][-1].content))


def create_app(graph=None) -> FastAPI:
    """graph=None: echter Graph mit Checkpointer aus den Einstellungen (Tests übergeben einen)."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if graph is not None:
            app.state.graph = graph
            yield
        else:
            with get_checkpointer() as checkpointer:
                app.state.graph = build_graph(checkpointer=checkpointer)  # einmal beim Start
                yield

    app = FastAPI(title="Support Bot", lifespan=lifespan)

    def unavailable() -> HTTPException:
        return HTTPException(503, "Der Dienst ist vorübergehend nicht erreichbar.")

    @app.get("/health")
    def health():
        if settings.checkpointer_backend == "postgres":
            try:
                psycopg.connect(settings.postgres_url, connect_timeout=2).close()
            except psycopg.OperationalError:
                raise unavailable()
        return {"status": "ok", "checkpointer": settings.checkpointer_backend}

    @app.post("/chat", response_model=ChatResponse)
    def chat(body: ChatRequest, request: Request):
        graph = request.app.state.graph
        config = {"configurable": {"thread_id": body.thread_id}}
        try:
            if graph.get_state(config).next:
                raise HTTPException(409, "Die Retoure wartet noch auf die Freigabe.")
            result = graph.invoke({"messages": [("user", body.message)]}, config)
        except psycopg.OperationalError:
            raise unavailable()
        return _to_response(result)

    @app.post("/review", response_model=ChatResponse)
    def review(body: ReviewRequest, request: Request):
        graph = request.app.state.graph
        config = {"configurable": {"thread_id": body.thread_id}}
        try:
            if not graph.get_state(config).next:
                raise HTTPException(409, "Für diesen Thread liegt keine offene Freigabe vor.")
            decision = "approve" if body.approved else "reject"
            result = graph.invoke(Command(resume=decision), config)
        except psycopg.OperationalError:
            raise unavailable()
        return _to_response(result)

    return app


app = create_app()
