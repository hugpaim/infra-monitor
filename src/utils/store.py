# src/utils/store.py
import sqlite3
import time
from pathlib import Path
from src.collectors.base import Metric


class MetricsStore:
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    labels TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_name_ts ON metrics(name, timestamp)")

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def save(self, metrics: list[Metric]):
        import json
        rows = [
            (m.name, float(m.value) if isinstance(m.value, (int, float)) else 0,
             m.unit, json.dumps(m.labels), m.timestamp)
            for m in metrics
        ]
        with self._conn() as conn:
            conn.executemany(
                "INSERT INTO metrics (name, value, unit, labels, timestamp) VALUES (?,?,?,?,?)",
                rows,
            )

    def latest(self, name: str) -> float | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT value FROM metrics WHERE name=? ORDER BY timestamp DESC LIMIT 1",
                (name,),
            ).fetchone()
        return row[0] if row else None

    def history(self, name: str, seconds: int = 300) -> list[tuple[float, float]]:
        since = time.time() - seconds
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT timestamp, value FROM metrics WHERE name=? AND timestamp>? ORDER BY timestamp",
                (name, since),
            ).fetchall()
        return rows

    def prune(self, older_than_seconds: int = 86400):
        cutoff = time.time() - older_than_seconds
        with self._conn() as conn:
            conn.execute("DELETE FROM metrics WHERE timestamp<?", (cutoff,))
