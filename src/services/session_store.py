import json
import time
from pathlib import Path

from src.models.session import Session

_SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sessions"


def _ensure_dir():
    _SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def save_session(session: Session) -> None:
    """Save a session to a JSON file."""
    _ensure_dir()
    session.updated_at = time.time()
    path = _SESSIONS_DIR / f"{session.session_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> Session | None:
    """Load a session by its ID. Returns None if not found."""
    path = _SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Session.from_dict(data)


def list_sessions() -> list[Session]:
    """List all saved sessions, sorted by most recently updated first."""
    _ensure_dir()
    sessions = []
    for path in _SESSIONS_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append(Session.from_dict(data))
        except (json.JSONDecodeError, KeyError):
            continue
    sessions.sort(key=lambda s: s.updated_at, reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session file. Returns True if deleted."""
    path = _SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False
