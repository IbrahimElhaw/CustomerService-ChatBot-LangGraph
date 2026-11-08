from contextlib import contextmanager

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from .config import settings


@contextmanager
def get_checkpointer() -> MemorySaver | PostgresSaver:
    """Liefert je nach Einstellung MemorySaver oder PostgresSaver.
    Als Context-Manager, damit die Postgres-Verbindung sauber geschlossen wird.
    """

    if settings.checkpointer_backend == "postgres":

        with PostgresSaver.from_conn_string(settings.postgres_url) as saver:
            saver.setup()  # legt die Tabellen an (idempotent)
            yield saver
    else:
        yield MemorySaver()