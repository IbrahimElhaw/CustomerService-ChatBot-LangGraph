import sqlite3
from .config import settings

DB_PATH = settings.data_dir / "orders.db"

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_email TEXT NOT NULL,
                status TEXT NOT NULL,
                carrier TEXT,
                tracking_number TEXT,
                estimated_arrival TEXT,
                total_eur REAL NOT NULL
            );
            DELETE FROM orders;
            INSERT INTO orders VALUES
              ('SN-1001', 'anna@example.com', 'shipped',   'DHL', 'JJD0001234', '2026-11-10', 59.90),
              ('SN-1002', 'ben@example.com',  'processing', NULL,  NULL,         '2026-11-14', 129.00),
              ('SN-1003', 'anna@example.com', 'delivered',  'DHL', 'JJD0005678', '2026-11-02', 24.50);
            """
        )