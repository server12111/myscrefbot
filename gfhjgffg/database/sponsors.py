import aiosqlite

DB = "database.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sponsors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                channel_link TEXT NOT NULL,
                title TEXT NOT NULL
            )
        """)
        await db.commit()


async def get_sponsors():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT * FROM sponsors"
        )
        return await cursor.fetchall()


async def add_sponsor(channel_id, channel_link, title):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO sponsors (
                channel_id,
                channel_link,
                title
            ) VALUES (?, ?, ?)
            """,
            (channel_id, channel_link, title)
        )
        await db.commit()


async def delete_sponsor(sponsor_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "DELETE FROM sponsors WHERE id = ?",
            (sponsor_id,)
        )
        await db.commit()