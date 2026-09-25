"""Create or promote a faculty account with a local password prompt.

Run from services/api after `python -m alembic upgrade head`:
    python scripts/create_faculty.py
"""
import asyncio
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.rbac import Role, user_roles
from app.models.user import User


async def main() -> None:
    email = input("Faculty email: ").strip().lower()
    full_name = input("Faculty full name: ").strip()
    password = getpass("Faculty password (8+ chars, upper and lower case): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 8 or password.lower() == password or password.upper() == password:
        raise SystemExit("Password must be 8+ characters and include upper and lower case letters")

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).options(selectinload(User.roles)).where(User.normalized_email == email))
        if not user:
            user = User(email=email, normalized_email=email, full_name=full_name, password_hash=hash_password(password), status="active", is_active=True)
            db.add(user)
            await db.flush()
        else:
            user.full_name = full_name or user.full_name
            user.password_hash = hash_password(password)
            user.is_active = True
            user.status = "active"
        role = await db.scalar(select(Role).where(Role.code == "faculty"))
        if role is None:
            raise SystemExit("faculty role is missing. Run python -m alembic upgrade head first.")
        assigned_role_id = await db.scalar(select(user_roles.c.role_id).where(user_roles.c.user_id == user.id, user_roles.c.role_id == role.id))
        if assigned_role_id is None:
            await db.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
        await db.commit()
        print(f"Faculty account ready: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
