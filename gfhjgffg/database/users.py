import aiosqlite

DB_NAME = "database.db"


async def create_users_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                verified INTEGER DEFAULT 0,
                referrer_id INTEGER,
                balance REAL DEFAULT 0,
                rewarded INTEGER DEFAULT 0,
                next_bonus INTEGER DEFAULT 0
            )
        """)

        columns = [
            ("rewarded", "INTEGER DEFAULT 0"),
            ("next_bonus", "INTEGER DEFAULT 0"),
            ("balance", "REAL DEFAULT 0")
        ]

        for column_name, column_type in columns:
            try:
                await db.execute(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                )
            except:
                pass

        await db.commit()


async def create_withdraw_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS withdraws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        try:
            await db.execute("ALTER TABLE withdraws ADD COLUMN status TEXT DEFAULT 'pending'")
        except Exception:
            pass
        await db.commit()


async def create_withdraw_request(user_id: int, amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO withdraws (user_id, amount, status)
            VALUES (?, ?, 'pending')
        """, (user_id, amount))

        await db.commit()

        return cursor.lastrowid


async def get_withdraw_request(request_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, user_id, amount, status FROM withdraws WHERE id = ?
        """, (request_id,))
        return await cursor.fetchone()


async def update_withdraw_status(request_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE withdraws SET status = ? WHERE id = ?
        """, (status, request_id))
        await db.commit()


async def add_user(user_id: int, referrer_id: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (
                user_id,
                referrer_id
            )
            VALUES (?, ?)
        """, (user_id, referrer_id))

        await db.commit()


async def is_verified(user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT verified
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return bool(result[0]) if result else False


async def set_verified(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET verified = 1
            WHERE user_id = ?
        """, (user_id,))

        await db.commit()


async def remove_verified(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET verified = 0
            WHERE user_id = ?
        """, (user_id,))

        await db.commit()


async def get_referrer(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT referrer_id
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return result[0] if result else None


async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
        """, (amount, user_id))

        await db.commit()


async def get_balance(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT balance
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return result[0] if result else 0


async def is_rewarded(user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT rewarded
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return bool(result[0]) if result else False


async def set_rewarded(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET rewarded = 1
            WHERE user_id = ?
        """, (user_id,))

        await db.commit()


async def get_referrals_count(referrer_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE referrer_id = ?
        """, (referrer_id,))

        result = await cursor.fetchone()

        return result[0] if result else 0


async def get_next_bonus(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT next_bonus
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return result[0] if result else 0


async def set_next_bonus(user_id: int, timestamp: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET next_bonus = ?
            WHERE user_id = ?
        """, (timestamp, user_id))

        await db.commit()


async def get_all_users() -> list:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]