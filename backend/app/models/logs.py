"""
DevFlow – Log ORM model.
Every action performed (deploy, user create, password reset, etc.)
is persisted here for the dashboard activity feed.
"""

from __future__ import annotations

import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.database import Base


class Log(Base):
    """Audit log entry for every DevOps action."""

    __tablename__ = "logs"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action: str = Column(String(255), nullable=False, index=True)
    status: str = Column(String(50), nullable=False, default="pending")
    detail: str = Column(Text, nullable=True)
    source: str = Column(String(50), nullable=False, default="api")  # "api" | "slack"
    timestamp: datetime.datetime = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Log id={self.id} action={self.action!r} status={self.status!r}>"

    def to_dict(self) -> dict:
        """Serialize the log to a plain dictionary for JSON responses."""
        return {
            "id": self.id,
            "action": self.action,
            "status": self.status,
            "detail": self.detail,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
