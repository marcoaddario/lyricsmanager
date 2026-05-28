from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Integer, ForeignKey, String, DateTime, Enum as SQLEnum,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class SharePermission(str, Enum):
    """Permission levels for shared setlists"""
    VIEW = "view"  # Read-only access
    EDIT = "edit"  # Can modify setlist


class SetlistShare(Base):
    """Shared access to a setlist with another user"""
    __tablename__ = "setlist_shares"
    __table_args__ = (UniqueConstraint("setlist_id", "shared_with_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    setlist_id: Mapped[int] = mapped_column(ForeignKey("setlists.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_with_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission: Mapped[SharePermission] = mapped_column(SQLEnum(SharePermission), default=SharePermission.VIEW, nullable=False)
    shared_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    # Relationships
    setlist: Mapped["Setlist"] = relationship("Setlist", back_populates="shares")
    shared_with_user: Mapped["User"] = relationship("User")
