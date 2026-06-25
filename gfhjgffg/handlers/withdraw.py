from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from config import ADMINS

from database.users import (
    get_balance,
    add_balance,
    create_withdraw_request
)

from keyboards.user_kb import (
    withdraw_kb,
    back_kb
)

router = Router()


@router.callback_query(F.data == "withdraw")
async def withdraw_menu(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/withdraw.png"),
        caption="Выберите количество звёзд для вывода:",
        reply_markup=withdraw_kb()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("withdraw_"))
async def withdraw_request(callback: CallbackQuery, bot: Bot):
    amount = int(callback.data.split("_")[1])

    balance = await get_balance(callback.from_user.id)

    if balance < amount:
        await callback.answer(
            "❌ У вас недостаточно звёзд для вывода!",
            show_alert=True
        )
        return

    await add_balance(callback.from_user.id, -amount)

    request_number = await create_withdraw_request(
        callback.from_user.id,
        amount
    )

    username = (
        f"@{callback.from_user.username}"
        if callback.from_user.username
        else callback.from_user.full_name
    )

    text = (
        f"📥 Заявка на вывод №{request_number}\n\n"
        f"⭐ Количество: {amount}\n"
        f"👤 Пользователь: {username}\n"
        f"🆔 ID: <code>{callback.from_user.id}</code>"
    )

    for admin_id in ADMINS:
        await bot.send_message(
            chat_id=admin_id,
            text=text,
            parse_mode="HTML"
        )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(
        "✅ Вы успешно отправили заявку на вывод.\n"
        "Подарок придёт вам в течение 16 часов.",
        reply_markup=back_kb()
    )

    await callback.answer()