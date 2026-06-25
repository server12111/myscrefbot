import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

# ================== DATABASE ==================
from database.sponsors import init_db
from database.users import (
    create_users_table,
    create_withdraw_table
)
from database.settings import (
    create_settings_table,
    create_bonus_table
)
from database.promocodes import create_promocodes_table

# ================== HANDLERS ==================
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.earn import router as earn_router
from handlers.bonus import router as bonus_router
from handlers.withdraw import router as withdraw_router
from handlers.promo import router as promo_router


async def main():
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()

    # ================== ROUTERS ==================
    dp.include_router(start_router)
    dp.include_router(earn_router)
    dp.include_router(bonus_router)
    dp.include_router(withdraw_router)
    dp.include_router(promo_router)
    dp.include_router(admin_router)

    # ================== DB INIT ==================
    await init_db()
    await create_users_table()
    await create_withdraw_table()
    await create_settings_table()
    await create_bonus_table()
    await create_promocodes_table()

    print("Bot started...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())