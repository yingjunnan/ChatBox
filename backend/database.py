import aiosqlite
from datetime import datetime

DATABASE = "chatbox.db"

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        """)
        await db.commit()

async def create_room(room_id: str, name: str, password: str = None):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO rooms (id, name, password, created_at) VALUES (?, ?, ?, ?)",
            (room_id, name, password, datetime.now().isoformat())
        )
        await db.commit()

async def get_rooms():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT id, name, password, created_at FROM rooms ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [{
                "id": row[0],
                "name": row[1],
                "has_password": row[2] is not None and row[2] != "",
                "created_at": row[3]
            } for row in rows]

async def get_room(room_id: str):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT id, name, password, created_at FROM rooms WHERE id = ?", (room_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "password": row[2], "created_at": row[3]}
            return None

async def save_message(room_id: str, username: str, content: str, message_type: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO messages (room_id, username, content, message_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (room_id, username, content, message_type, datetime.now().isoformat())
        )
        await db.commit()
