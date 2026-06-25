from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from keyboards.user_kb import main_menu, earn_kb
from database.settings import get_ref_reward

router = Router()

@router.callback_query(F.data == "earn")
async def earn(callback: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()

    ref_reward = await get_ref_reward()

    ref_link = (
        f"https://t.me/{bot_info.username}"
        f"?start={callback.from_user.id}"
    )

    text = (
        f"За каждого друга, который перейдет по твоей ссылке, ты получаешь +{ref_reward} ⭐️\n\n"
        f"🔗 Твоя реферальная ссылка:\n{ref_link}\n\n"
        "🚀 Приглашай по этой ссылке друзей, отправляй её во все чаты и зарабатывай Звёзды!"
    )

    await callback.message.delete()

    await callback.message.answer_photo(
        photo=FSInputFile("images/referral.png"),
        caption=text,
        reply_markup=earn_kb()
    )

    await callback.answer()


@router.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.delete()

    await callback.message.answer_photo(
        photo=FSInputFile("images/menu.png"),
        caption="✨ Добро пожаловать!",
        reply_markup=main_menu()
    )

    await callback.answer()