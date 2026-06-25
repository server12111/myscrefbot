import aiosqlite

DB_NAME = "database.db"


async def create_promocodes_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY,
                reward REAL NOT NULL,
                uses INTEGER NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS promo_activations (
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                PRIMARY KEY (user_id, code)
            )
        """)

        await db.commit()


async def add_promocode(code: str, reward: float, uses: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO promocodes (code, reward, uses)
            VALUES (?, ?, ?)
        """, (code.upper(), reward, uses))

        await db.commit()


async def delete_promocode(code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            DELETE FROM promocodes
            WHERE code = ?
        """, (code.upper(),))

        await db.commit()


async def get_promocode(code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT reward, uses
            FROM promocodes
            WHERE code = ?
        """, (code.upper(),))

        return await cursor.fetchone()


async def activate_promocode(user_id: int, code: str):
    code = code.upper()

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT reward, uses
            FROM promocodes
            WHERE code = ?
        """, (code,))

        promo = await cursor.fetchone()

        if not promo:
            return False, 0

        reward, uses = promo

        if uses <= 0:
            return False, 0

        cursor = await db.execute("""
            SELECT 1
            FROM promo_activations
            WHERE user_id = ? AND code = ?
        """, (user_id, code))

        if await cursor.fetchone():
            return False, 0

        await db.execute("""
            INSERT INTO promo_activations (user_id, code)
            VALUES (?, ?)
        """, (user_id, code))

        await db.execute("""
            UPDATE promocodes
            SET uses = uses - 1
            WHERE code = ?
        """, (code,))

        await db.commit()

        return True, reward


async def get_all_promocodes():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT code, reward, uses
            FROM promocodes
        """)

        return await cursor.fetchall()