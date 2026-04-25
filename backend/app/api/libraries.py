from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import Library, Song, User
from app.schemas.schemas import LibraryCreate, LibraryUpdate, LibraryOut

router = APIRouter(prefix="/libraries", tags=["libraries"])


async def _library_with_count(db, library):
    count_result = await db.execute(
        select(func.count()).where(Song.library_id == library.id)
    )
    library_out = LibraryOut.model_validate(library)
    library_out.song_count = count_result.scalar_one()
    return library_out


@router.get("/", response_model=List[LibraryOut])
async def list_libraries(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        result = await db.execute(select(Library).order_by(Library.name))
    else:
        result = await db.execute(
            select(Library).where(
                (Library.owner_id == current_user.id) | (Library.is_global == True)
            ).order_by(Library.name)
        )
    libraries = result.scalars().all()
    return [await _library_with_count(db, lib) for lib in libraries]


@router.post("/", response_model=LibraryOut, status_code=status.HTTP_201_CREATED)
async def create_library(
    body: LibraryCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if body.is_global and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create global libraries")
    library = Library(
        name=body.name,
        description=body.description,
        is_global=body.is_global,
        owner_id=None if body.is_global else current_user.id,
    )
    db.add(library)
    await db.flush()
    return await _library_with_count(db, library)


@router.get("/{library_id}", response_model=LibraryOut)
async def get_library(
    library_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Library).where(Library.id == library_id))
    lib = result.scalar_one_or_none()
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    if not current_user.is_admin and lib.owner_id != current_user.id and not lib.is_global:
        raise HTTPException(status_code=403, detail="Access denied")
    return await _library_with_count(db, lib)


@router.patch("/{library_id}", response_model=LibraryOut)
async def update_library(
    library_id: int, body: LibraryUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Library).where(Library.id == library_id))
    lib = result.scalar_one_or_none()
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    if not current_user.is_admin and lib.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(lib, k, v)
    return await _library_with_count(db, lib)


@router.delete("/{library_id}", status_code=204)
async def delete_library(
    library_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Library).where(Library.id == library_id))
    lib = result.scalar_one_or_none()
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    if not current_user.is_admin and lib.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.delete(lib)
