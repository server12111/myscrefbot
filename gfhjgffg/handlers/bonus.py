import time

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from database.settings import get_bonus_reward
from database.users import add_balance, get_next_bonus, set_next_bonus
from keyboards.user_kb import back_kb

router = Router()


@router.callback_query(F.data == "bonus")
async def bonus(callback: CallbackQuery):
    user_id = callback.from_user.id

    now = int(time.time())
    last_bonus = await get_next_bonus(user_id)

    cooldown = 4 * 60 * 60

    # ❌ cooldown
    if now < last_bonus:
        remaining = last_bonus - now
        h = remaining // 3600
        m = (remaining % 3600) // 60

        await callback.answer(
            f"Бонус будет доступен через {h}ч {m}мин",
            show_alert=True
        )
        return

    reward = await get_bonus_reward()

    await add_balance(user_id, reward)
    await set_next_bonus(user_id, now + cooldown)

    # 🔥 1) БОЛЬШОЕ УВЕДОМЛЕНИЕ (ТО ЧТО ТЫ ХОЧЕШЬ)
    await callback.answer(
        f"🎉 Вы получили {reward}⭐ бонуса!",
        show_alert=True
    )

    # 📸 2) ПОТОМ ФОТО + ТЕКСТ
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/bonus.png"),
        caption=f"Вы получили {reward}⭐ бонуса!",
        reply_markup=back_kb()
    )