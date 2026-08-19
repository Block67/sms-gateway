"""Crée un client (ou un admin) et affiche sa clé API.

Usage:
    python -m scripts.create_user client@example.com
    python -m scripts.create_user admin@example.com --admin
    python -m scripts.create_user test@example.com --test
"""

import asyncio
import sys

from src.database import async_session_factory
from src.users.service import create_user


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.create_user <email> [--admin] [--test]")
        sys.exit(1)

    email = sys.argv[1]
    is_admin = "--admin" in sys.argv
    is_test = "--test" in sys.argv

    async with async_session_factory() as db:
        user = await create_user(db, email=email, is_test=is_test)
        if is_admin:
            user.is_admin = True
            await db.commit()

        print(f"Utilisateur créé : {user.email}")
        print(f"Clé API (X-API-Key) : {user.api_key}")


if __name__ == "__main__":
    asyncio.run(main())
