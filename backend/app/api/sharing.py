from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import Setlist, SetlistShare, User
from app.schemas.schemas import SetlistShareCreate, SetlistShareUpdate, SetlistShareOut

router = APIRouter(prefix="/setlists", tags=["sharing"])


@router.get("/{setlist_id}/shares", response_model=List[SetlistShareOut])
async def list_shares(
    setlist_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all shares for a setlist (owner only)"""
    result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    
    shares_result = await db.execute(
        select(SetlistShare)
        .options(selectinload(SetlistShare.shared_with_user))
        .where(SetlistShare.setlist_id == setlist_id)
    )
    return shares_result.scalars().all()


@router.post("/{setlist_id}/shares", response_model=SetlistShareOut, status_code=status.HTTP_201_CREATED)
async def add_share(
    setlist_id: int, body: SetlistShareCreate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Share a setlist with another user (owner only)"""
    result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    
    # Verify user exists
    user_result = await db.execute(
        select(User).where(User.id == body.shared_with_user_id)
    )
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent sharing with self
    if body.shared_with_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share with yourself")
    
    # Check if already shared
    existing = await db.execute(
        select(SetlistShare).where(
            SetlistShare.setlist_id == setlist_id,
            SetlistShare.shared_with_user_id == body.shared_with_user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already shared with this user")
    
    share = SetlistShare(
        setlist_id=setlist_id,
        shared_with_user_id=body.shared_with_user_id,
        permission=body.permission
    )
    db.add(share)
    await db.flush()
    
    result = await db.execute(
        select(SetlistShare)
        .options(selectinload(SetlistShare.shared_with_user))
        .where(SetlistShare.id == share.id)
    )
    return result.scalar_one()


@router.patch("/{setlist_id}/shares/{share_id}", response_model=SetlistShareOut)
async def update_share(
    setlist_id: int, share_id: int, body: SetlistShareUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Update share permission (owner only)"""
    result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    
    share_result = await db.execute(
        select(SetlistShare).where(SetlistShare.id == share_id, SetlistShare.setlist_id == setlist_id)
    )
    share = share_result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    share.permission = body.permission
    
    result = await db.execute(
        select(SetlistShare)
        .options(selectinload(SetlistShare.shared_with_user))
        .where(SetlistShare.id == share.id)
    )
    return result.scalar_one()


@router.delete("/{setlist_id}/shares/{share_id}", status_code=204)
async def remove_share(
    setlist_id: int, share_id: int,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Remove a share (owner only)"""
    result = await db.execute(
        select(Setlist).where(Setlist.id == setlist_id, Setlist.owner_id == current_user.id)
    )
    setlist = result.scalar_one_or_none()
    if not setlist:
        raise HTTPException(status_code=404, detail="Setlist not found")
    
    share_result = await db.execute(
        select(SetlistShare).where(SetlistShare.id == share_id, SetlistShare.setlist_id == setlist_id)
    )
    share = share_result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    await db.delete(share)
