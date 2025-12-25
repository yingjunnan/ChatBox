import aiosqlite
from datetime import datetime
from typing import Optional
from models import User
from auth import hash_password

DATABASE = "chatbox.db"

async def create_user(username: str, password: str, display_name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
    async with aiosqlite.connect(DATABASE) as db:
        password_hash = hash_password(password)
        now = datetime.now().isoformat()
        try:
            cursor = await db.execute(
                "INSERT INTO users (username, password_hash, display_name, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, password_hash, display_name, email, now, now)
            )
            await db.commit()
            user_id = cursor.lastrowid
            return await get_user_by_id(user_id)
        except aiosqlite.IntegrityError:
            return None

async def get_user_by_username(username: str) -> Optional[User]:
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT id, username, password_hash, display_name, email, avatar_url, created_at, updated_at FROM users WHERE username = ?",
            (username,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    display_name=row[3],
                    email=row[4],
                    avatar_url=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
            return None

async def get_user_by_id(user_id: int) -> Optional[User]:
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT id, username, password_hash, display_name, email, avatar_url, created_at, updated_at FROM users WHERE id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    display_name=row[3],
                    email=row[4],
                    avatar_url=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
            return None

async def update_user(user_id: int, display_name: Optional[str] = None, email: Optional[str] = None, avatar_url: Optional[str] = None) -> Optional[User]:
    async with aiosqlite.connect(DATABASE) as db:
        updates = []
        params = []
        if display_name is not None:
            updates.append("display_name = ?")
            params.append(display_name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if avatar_url is not None:
            updates.append("avatar_url = ?")
            params.append(avatar_url)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(user_id)

            await db.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                params
            )
            await db.commit()

        return await get_user_by_id(user_id)

async def save_refresh_token(user_id: int, token: str, expires_at: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (user_id, token, expires_at, datetime.now().isoformat())
        )
        await db.commit()

async def verify_refresh_token(token: str) -> Optional[int]:
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT user_id, expires_at FROM refresh_tokens WHERE token = ?",
            (token,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                user_id, expires_at = row
                if datetime.fromisoformat(expires_at) > datetime.now():
                    return user_id
            return None

async def delete_refresh_token(token: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM refresh_tokens WHERE token = ?", (token,))
        await db.commit()
