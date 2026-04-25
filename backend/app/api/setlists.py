from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import Setlist, SetlistItem, Song, User
from app.schemas.schemas import (
    SetlistCreate, SetlistUpdate, SetlistOut, SetlistSummary, SetlistItemCreate
)

router = APIRouter(prefix="/setlists", tags=["setlists"])


@router.get("/", response_model=List[SetlistSummary])
async def list_setlists(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Setlist).where(Setlist.owner_id == current_user.id).order_by(Setlist.event_date.desc().nullslast())
    )
    setlists = result.scalars().all()
    out = []
    for s in setlists:
        count = await db.execute(select(func.count()).where(SetlistItem.setlist_id == s.id))
        summary = SetlistSummary.model_validate(s)
        summary.song_count = count.scalar_one()
        out.append(summary)
    return out


@router.post("/", response_model=SetlistOut, status_code=status.HTTP_201_CREATED)
async def create_setlist(
    body: SetlistCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setlist = Setlist(owner_id=current_user.id, **body.model_dump())
    db.add(setlist)
    await db.flush()
    result = await db.execute(
        select(Setlist).options(selectinload(Setlist.items).selectinload(SetlistItem.song))
        .where(Setlist.id == setlist.id)
    )
    return result.scalar_one()


@router.get("/{setlist_id}", response_model=SetlistOut)
async def get_setlist(
    setlist_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.items).selectinload(SetlistItem.song))
        .where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    return setlist


@router.patch("/{setlist_id}", response_model=SetlistOut)
async def update_setlist(
    setlist_id: int, body: SetlistUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id))
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(setlist, k, v)
    result = await db.execute(
        select(Setlist).options(selectinload(Setlist.items).selectinload(SetlistItem.song))
        .where(Setlist.id == setlist_id)
    )
    return result.scalar_one()


@router.delete("/{setlist_id}", status_code=204)
async def delete_setlist(
    setlist_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id))
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    await db.delete(setlist)


@router.put("/{setlist_id}/items", response_model=SetlistOut)
async def replace_items(
    setlist_id: int, items: List[SetlistItemCreate],
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Setlist not found")

    await db.execute(delete(SetlistItem).where(SetlistItem.setlist_id == setlist_id))

    for item in items:
        song = await db.get(Song, item.song_id)
        if not song:
            raise HTTPException(status_code=404, detail=f"Song {item.song_id} not found")
        db.add(SetlistItem(setlist_id=setlist_id, **item.model_dump()))

    await db.flush()
    result = await db.execute(
        select(Setlist).options(selectinload(Setlist.items).selectinload(SetlistItem.song))
        .where(Setlist.id == setlist_id)
    )
    return result.scalar_one()


@router.get("/{setlist_id}/download")
async def download_setlist(
    setlist_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return full setlist with all lyrics for offline caching."""
    result = await db.execute(
        select(Setlist)
        .options(selectinload(Setlist.items).selectinload(SetlistItem.song))
        .where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    return SetlistOut.model_validate(setlist)
