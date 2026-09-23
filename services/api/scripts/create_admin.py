"""Create or promote an administrator without putting a password in source control.

Run from services/api after `alembic upgrade head`:
    python scripts/create_admin.py
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
    email = input("Admin email: ").strip().lower()
    full_name = input("Admin full name: ").strip()
    password = getpass("Admin password (8+ chars, upper and lower case): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    if len(password) < 8 or password.lower() == password or password.upper() == password:
        raise SystemExit("Password must be 8+ characters and include upper and lower case letters")

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).options(selectinload(User.roles)).where(User.normalized_email == email))
        if not user:
            user = User(
                email=email,
                normalized_email=email,
                full_name=full_name,
                password_hash=hash_password(password),
                status="active",
                is_active=True,
            )
            db.add(user)
            await db.flush()
        else:
            user.full_name = full_name or user.full_name
            user.password_hash = hash_password(password)
            user.is_active = True
            user.status = "active"

        role = await db.scalar(select(Role).where(Role.code == "super_admin"))
        if role is None:
            raise SystemExit("super_admin role is missing. Run alembic upgrade head first.")
        assigned_role_id = await db.scalar(
            select(user_roles.c.role_id).where(
                user_roles.c.user_id == user.id,
                user_roles.c.role_id == role.id,
            )
        )
        if assigned_role_id is None:
            await db.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
        await db.commit()
        print(f"Administrator ready: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
