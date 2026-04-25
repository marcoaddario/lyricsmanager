from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.auth import require_admin
from app.core.config import get_settings
from app.models.user import User, Library, Song, Setlist
from app.schemas.schemas import StorageInfo

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


@router.get("/storage", response_model=StorageInfo)
async def storage_info(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    song_count = (await db.execute(select(func.count()).select_from(Song))).scalar_one()
    lib_count = (await db.execute(select(func.count()).select_from(Library))).scalar_one()
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar_one()

    # Estimate storage from lyrics text
    size_result = await db.execute(select(func.sum(func.length(Song.lyrics))))
    used_bytes = size_result.scalar_one() or 0

    return StorageInfo(
        used_mb=round(used_bytes / 1024 / 1024, 2),
        max_mb=settings.max_storage_mb,
        song_count=song_count,
        library_count=lib_count,
        user_count=user_count,
    )