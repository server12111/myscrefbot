import aiosqlite

DB_NAME = "database.db"


async def create_bonus_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bonus (
                user_id INTEGER PRIMARY KEY,
                next_bonus INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def get_next_bonus(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT next_bonus FROM bonus WHERE user_id=?
        """, (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0


async def set_next_bonus(user_id: int, ts: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO bonus (user_id, next_bonus)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET next_bonus=excluded.next_bonus
        """, (user_id, ts))
        await db.commit()