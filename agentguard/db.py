import json, sqlite3
from pathlib import Path
from .config import settings
def _path():
    url=settings.database_url
    if not url.startswith("sqlite:///"): raise RuntimeError("This starter currently supports SQLite; configure a production DB adapter before deployment.")
    p=Path(url.removeprefix("sqlite:///")); p.parent.mkdir(parents=True,exist_ok=True); return p
def init_db():
    with sqlite3.connect(_path()) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS audit_events (
          id TEXT PRIMARY KEY, created_at TEXT NOT NULL, action_type TEXT NOT NULL,
          decision TEXT NOT NULL, retrieval_ms REAL NOT NULL, total_ms REAL NOT NULL,
          backend TEXT NOT NULL, payload_json TEXT NOT NULL)""")
def write_audit(event):
    with sqlite3.connect(_path()) as c:
        c.execute("INSERT INTO audit_events VALUES(?,?,?,?,?,?,?,?)",
        (event["id"],event["created_at"],event["action_type"],event["decision"],event["retrieval_ms"],event["total_ms"],event["backend"],json.dumps(event["payload"])))
def recent_audit(limit=50):
    with sqlite3.connect(_path()) as c:
        c.row_factory=sqlite3.Row
        return [dict(r) for r in c.execute("SELECT id,created_at,action_type,decision,retrieval_ms,total_ms,backend FROM audit_events ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()]
