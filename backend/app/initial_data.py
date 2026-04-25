"""
Creates the first admin user if it doesn't exist.
Run once on startup via the Dockerfile CMD.
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.auth import hash_password
from app.core.config import get_settings
from app.models.user import User, Library

settings = get_settings()


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.first_admin_email))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping seed.")
            return

        admin = User(
            email=settings.first_admin_email,
            username="admin",
            hashed_password=hash_password(settings.first_admin_password),
            display_name="Administrator",
            is_admin=True,
        )
        db.add(admin)
        await db.flush()

        # Create a default global library
        global_lib = Library(name="Global Library", description="Shared songs for everyone", is_global=True)
        db.add(global_lib)
        await db.commit()
        print(f"Created admin user: {settings.first_admin_email}")
        print("Created Global Library")


if __name__ == "__main__":
    asyncio.run(main())
