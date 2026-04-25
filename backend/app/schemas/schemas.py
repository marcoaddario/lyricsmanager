from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    identifier: str  # Can be email or username
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    display_name: Optional[str] = None
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    color_theme: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    email: str
    username: str
    display_name: Optional[str]
    is_active: bool
    is_admin: bool
    color_theme: str
    created_at: datetime


# ── Libraries ─────────────────────────────────────────────────────────────────

class LibraryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_global: bool = False


class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LibraryOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: Optional[str]
    owner_id: Optional[int]
    is_global: bool
    created_at: datetime
    song_count: int = 0


# ── Songs ─────────────────────────────────────────────────────────────────────

class SongCreate(BaseModel):
    title: str
    artist: Optional[str] = None
    lyrics: str = ""
    key: Optional[str] = None
    tempo: Optional[int] = None
    notes: Optional[str] = None


class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    lyrics: Optional[str] = None
    key: Optional[str] = None
    tempo: Optional[int] = None
    notes: Optional[str] = None


class SongOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    artist: Optional[str]
    lyrics: str
    key: Optional[str]
    tempo: Optional[int]
    notes: Optional[str]
    library_id: int
    updated_at: datetime


class SongSummary(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    artist: Optional[str]
    key: Optional[str]
    library_id: int
    updated_at: datetime


# ── Setlists ──────────────────────────────────────────────────────────────────

class SetlistItemCreate(BaseModel):
    song_id: int
    position: int
    transpose_key: Optional[str] = None
    notes: Optional[str] = None


class SetlistItemOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    song_id: int
    position: int
    transpose_key: Optional[str]
    notes: Optional[str]
    song: SongOut


class SetlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None


class SetlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None


class SetlistOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: Optional[str]
    event_date: Optional[datetime]
    owner_id: int
    created_at: datetime
    items: List[SetlistItemOut] = []


class SetlistSummary(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: Optional[str]
    event_date: Optional[datetime]
    created_at: datetime
    song_count: int = 0


# ── Storage ───────────────────────────────────────────────────────────────────

class StorageInfo(BaseModel):
    used_mb: float
    max_mb: int
    song_count: int
    library_count: int
    user_count: int
