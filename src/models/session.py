from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path


def _file_hash(file_path: str) -> str:
    """Compute a short SHA-256 hash of a file for identity tracking."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


@dataclass
class Session:
    """A translation session linking a document to its translations."""
    session_id: str
    document_path: str
    document_hash: str
    document_name: str
    paragraph_count: int
    translations: dict[int, str] = field(default_factory=dict)
    focused_index: int = 0
    created_at: float = 0.0
    updated_at: float = 0.0

    @staticmethod
    def create_new(file_path: str, paragraph_count: int) -> Session:
        now = time.time()
        doc_path = str(Path(file_path).resolve())
        return Session(
            session_id=f"{Path(file_path).stem}_{int(now)}",
            document_path=doc_path,
            document_hash=_file_hash(file_path),
            document_name=Path(file_path).name,
            paragraph_count=paragraph_count,
            translations={},
            focused_index=0,
            created_at=now,
            updated_at=now,
        )

    @property
    def translated_count(self) -> int:
        return sum(1 for t in self.translations.values() if t.strip())

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "document_path": self.document_path,
            "document_hash": self.document_hash,
            "document_name": self.document_name,
            "paragraph_count": self.paragraph_count,
            "translations": {str(k): v for k, v in self.translations.items()},
            "focused_index": self.focused_index,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> Session:
        return Session(
            session_id=data["session_id"],
            document_path=data["document_path"],
            document_hash=data["document_hash"],
            document_name=data["document_name"],
            paragraph_count=data["paragraph_count"],
            translations={int(k): v for k, v in data.get("translations", {}).items()},
            focused_index=data.get("focused_index", 0),
            created_at=data.get("created_at", 0.0),
            updated_at=data.get("updated_at", 0.0),
        )
