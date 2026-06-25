import aiosqlite

DB_NAME = "database.db"


# ================= SETTINGS =================
async def create_settings_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value REAL
            )
        """)

        await db.execute("""
            INSERT OR IGNORE INTO settings (key, value)
            VALUES ('ref_reward', 6)
        """)

        await db.execute("""
            INSERT OR IGNORE INTO settings (key, value)
            VALUES ('bonus_reward', 0.6)
        """)

        await db.commit()


# ================= REF =================
async def get_ref_reward():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT value FROM settings WHERE key='ref_reward'
        """)
        row = await cursor.fetchone()
        return float(row[0]) if row else 6.0


async def set_ref_reward(amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE settings SET value=? WHERE key='ref_reward'
        """, (amount,))
        await db.commit()


# ================= BONUS REWARD =================
async def get_bonus_reward():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT value FROM settings WHERE key='bonus_reward'
        """)
        row = await cursor.fetchone()
        return float(row[0]) if row else 0.6


async def set_bonus_reward(amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE settings SET value=? WHERE key='bonus_reward'
        """, (amount,))
        await db.commit()


# ================= BONUS TABLE =================
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


async def set_next_bonus(user_id: int, timestamp: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO bonus (user_id, next_bonus)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET next_bonus=excluded.next_bonus
        """, (user_id, timestamp))
        await db.commit()