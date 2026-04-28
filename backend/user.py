from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    color_theme: Mapped[str] = mapped_column(String(50), default="dark")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    libraries: Mapped[List["Library"]] = relationship("Library", back_populates="owner", cascade="all, delete-orphan")
    setlists: Mapped[List["Setlist"]] = relationship("Setlist", back_populates="owner", cascade="all, delete-orphan")


class Library(Base):
    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner: Mapped[Optional["User"]] = relationship("User", back_populates="libraries")
    songs: Mapped[List["Song"]] = relationship("Song", back_populates="library", cascade="all, delete-orphan")


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    artist: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    lyrics: Mapped[str] = mapped_column(Text, nullable=False, default="")
    key: Mapped[Optional[str]] = mapped_column(String(10))
    tempo: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    library_id: Mapped[int] = mapped_column(ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    library: Mapped["Library"] = relationship("Library", back_populates="songs")
    setlist_items: Mapped[List["SetlistItem"]] = relationship("SetlistItem", back_populates="song")


class Setlist(Base):
    __tablename__ = "setlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    event_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="setlists")
    items: Mapped[List["SetlistItem"]] = relationship(
        "SetlistItem", back_populates="setlist",
        cascade="all, delete-orphan", order_by="SetlistItem.position"
    )


class SetlistItem(Base):
    __tablename__ = "setlist_items"
    __table_args__ = (UniqueConstraint("setlist_id", "position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    setlist_id: Mapped[int] = mapped_column(ForeignKey("setlists.id", ondelete="CASCADE"), nullable=False)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    transpose_key: Mapped[Optional[str]] = mapped_column(String(10))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    setlist: Mapped["Setlist"] = relationship("Setlist", back_populates="items")
    song: Mapped["Song"] = relationship("Song", back_populates="setlist_items")
