from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import Library, Song, User
from app.schemas.schemas import SongCreate, SongUpdate, SongOut, SongSummary

router = APIRouter(prefix="/libraries/{library_id}/songs", tags=["songs"])


async def _get_accessible_library(library_id: int, db: AsyncSession, current_user: User) -> Library:
    result = await db.execute(select(Library).where(Library.id == library_id))
    lib = result.scalar_one_or_none()
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    if not current_user.is_admin and lib.owner_id != current_user.id and not lib.is_global:
        raise HTTPException(status_code=403, detail="Access denied")
    return lib


@router.get("/", response_model=List[SongSummary])
async def list_songs(
    library_id: int,
    q: Optional[str] = Query(None, description="Search title or artist"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_accessible_library(library_id, db, current_user)
    query = select(Song).where(Song.library_id == library_id)
    if q:
        query = query.where(or_(Song.title.ilike(f"%{q}%"), Song.artist.ilike(f"%{q}%")))
    result = await db.execute(query.order_by(Song.title))
    return result.scalars().all()


@router.post("/", response_model=SongOut, status_code=status.HTTP_201_CREATED)
async def create_song(
    library_id: int, body: SongCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lib = await _get_accessible_library(library_id, db, current_user)
    if lib.is_global and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can add songs to global libraries")
    song = Song(library_id=library_id, **body.model_dump())
    db.add(song)
    await db.flush()
    return song


@router.get("/{song_id}", response_model=SongOut)
async def get_song(
    library_id: int, song_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await _get_accessible_library(library_id, db, current_user)
    result = await db.execute(select(Song).where(Song.id == song_id, Song.library_id == library_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.patch("/{song_id}", response_model=SongOut)
async def update_song(
    library_id: int, song_id: int, body: SongUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    lib = await _get_accessible_library(library_id, db, current_user)
    if lib.is_global and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can edit songs in global libraries")
    result = await db.execute(select(Song).where(Song.id == song_id, Song.library_id == library_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(song, k, v)
    return song


@router.delete("/{song_id}", status_code=204)
async def delete_song(
    library_id: int, song_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lib = await _get_accessible_library(library_id, db, current_user)
    if lib.is_global and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete songs from global libraries")
    result = await db.execute(select(Song).where(Song.id == song_id, Song.library_id == library_id))
    song = result.scalar_one_or_none()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    await db.delete(song)
