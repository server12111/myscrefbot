from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMINS

from database.users import (
    get_balance,
    add_balance,
    create_withdraw_request,
    get_withdraw_request,
    update_withdraw_status,
)

from keyboards.user_kb import (
    withdraw_kb,
    back_kb
)

router = Router()


def admin_withdraw_kb(request_id: int, user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Одобрить",
            callback_data=f"wd_approve:{request_id}:{user_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отклонить",
            callback_data=f"wd_reject:{request_id}:{user_id}"
        ),
    ]])


@router.callback_query(F.data == "withdraw")
async def withdraw_menu(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
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

    request_id = await create_withdraw_request(callback.from_user.id, amount)

    username = (
        f"@{callback.from_user.username}"
        if callback.from_user.username
        else callback.from_user.full_name
    )

    text = (
        f"📥 Заявка на вывод №{request_id}\n\n"
        f"⭐ Количество: {amount}\n"
        f"👤 Пользователь: {username}\n"
        f"🆔 ID: <code>{callback.from_user.id}</code>"
    )

    for admin_id in ADMINS:
        await bot.send_message(
            chat_id=admin_id,
            text=text,
            parse_mode="HTML",
            reply_markup=admin_withdraw_kb(request_id, callback.from_user.id)
        )

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        "✅ Заявка на вывод отправлена.\n"
        "Подарок придёт в течение 16 часов.",
        reply_markup=back_kb()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("wd_approve:"))
async def approve_withdraw(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMINS:
        return

    _, request_id, user_id = callback.data.split(":")
    request_id, user_id = int(request_id), int(user_id)

    row = await get_withdraw_request(request_id)

    if not row:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    if row[3] != "pending":
        await callback.answer("Заявка уже обработана.", show_alert=True)
        return

    await update_withdraw_status(request_id, "approved")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Одобрено</b>",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            user_id,
            f"✅ Ваша заявка на вывод №{request_id} одобрена!\n"
            f"Звёзды придут в течение 16 часов. 🎁"
        )
    except Exception:
        pass

    await callback.answer("Одобрено!")


@router.callback_query(F.data.startswith("wd_reject:"))
async def reject_withdraw(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMINS:
        return

    _, request_id, user_id = callback.data.split(":")
    request_id, user_id = int(request_id), int(user_id)

    row = await get_withdraw_request(request_id)

    if not row:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    if row[3] != "pending":
        await callback.answer("Заявка уже обработана.", show_alert=True)
        return

    await update_withdraw_status(request_id, "rejected")
    await add_balance(user_id, row[2])  # возвращаем баланс

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Отклонено</b>",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            user_id,
            f"❌ Ваша заявка на вывод №{request_id} отклонена.\n"
            f"⭐ {int(row[2])} звёзд возвращены на ваш баланс."
        )
    except Exception:
        pass

    await callback.answer("Отклонено!")
