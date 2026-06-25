import asyncio
import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMINS

from states.admin_states import (
    AddSponsor,
    ChangeReward,
    ChangeBonus,
    Broadcast,
    ChangePhoto,
)

from keyboards.admin_kb import (
    admin_panel_kb,
    photos_kb,
    delete_sponsors_kb,
    delete_promos_kb,
    PHOTO_LABELS,
)

from database.sponsors import (
    add_sponsor,
    get_sponsors,
    delete_sponsor
)

from database.settings import (
    get_ref_reward,
    set_ref_reward,
    get_bonus_reward,
    set_bonus_reward
)

from database.promocodes import (
    add_promocode,
    delete_promocode,
    get_all_promocodes
)

from database.users import get_all_users

router = Router()


class AddPromo(StatesGroup):
    code = State()
    reward = State()
    uses = State()


# ===================== АДМИН ПАНЕЛЬ =====================

@router.message(Command("apanel", "admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMINS:
        return

    await message.answer(
        "⚙️ Админ-панель",
        reply_markup=admin_panel_kb()
    )


# ===================== СПОНСОРЫ =====================

@router.callback_query(F.data == "add_sponsor")
async def add_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    await state.set_state(AddSponsor.channel_id)

    await callback.message.answer(
        "Отправьте ID канала:"
    )

    await callback.answer()


@router.message(AddSponsor.channel_id)
async def get_channel_id(message: Message, state: FSMContext):
    await state.update_data(channel_id=message.text)

    await state.set_state(AddSponsor.channel_link)

    await message.answer(
        "Отправьте ссылку на канал:"
    )


@router.message(AddSponsor.channel_link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(channel_link=message.text)

    await state.set_state(AddSponsor.title)

    await message.answer(
        "Введите название кнопки:"
    )


@router.message(AddSponsor.title)
async def save_sponsor(message: Message, state: FSMContext):
    data = await state.get_data()

    await add_sponsor(
        channel_id=data["channel_id"],
        channel_link=data["channel_link"],
        title=message.text
    )

    await state.clear()

    await message.answer(
        "✅ Спонсор добавлен"
    )


@router.callback_query(F.data == "list_sponsors")
async def list_sponsors(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    sponsors = await get_sponsors()

    if not sponsors:
        await callback.answer(
            "Список пуст",
            show_alert=True
        )
        return

    text = "📋 Спонсоры:\n\n"

    for sponsor in sponsors:
        text += (
            f"ID: {sponsor[0]}\n"
            f"Название: {sponsor[3]}\n\n"
        )

    reward = await get_ref_reward()
    bonus = await get_bonus_reward()

    text += (
        f"⭐ Награда за реферала: {reward}\n"
        f"🎁 Бонус: {bonus}"
    )

    await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data == "delete_sponsor")
async def delete_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    sponsors = await get_sponsors()

    if not sponsors:
        await callback.answer(
            "Список пуст",
            show_alert=True
        )
        return

    await callback.message.answer(
        "Выберите спонсора:",
        reply_markup=delete_sponsors_kb(sponsors)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("delete_sponsor_"))
async def delete_item(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    sponsor_id = int(
        callback.data.replace(
            "delete_sponsor_",
            ""
        )
    )

    await delete_sponsor(sponsor_id)

    await callback.message.edit_text(
        "✅ Спонсор удалён"
    )

    await callback.answer()


# ===================== НАГРАДА =====================

@router.callback_query(F.data == "change_ref_reward")
async def change_reward(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    reward = await get_ref_reward()

    await callback.message.answer(
        f"Текущая награда: {reward}⭐\n\n"
        "Введите новую награду:"
    )

    await state.set_state(ChangeReward.amount)

    await callback.answer()


@router.message(ChangeReward.amount)
async def save_reward(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите число.")
        return

    await set_ref_reward(amount)

    await state.clear()

    await message.answer(
        f"✅ Награда обновлена: {amount}⭐"
    )


# ===================== БОНУС =====================

@router.callback_query(F.data == "change_bonus_reward")
async def change_bonus(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    bonus = await get_bonus_reward()

    await callback.message.answer(
        f"Текущий бонус: {bonus}⭐\n\n"
        "Введите новый бонус:"
    )

    await state.set_state(ChangeBonus.amount)

    await callback.answer()


@router.message(ChangeBonus.amount)
async def save_bonus(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(
            "Введите число. Например: 0.6"
        )
        return

    await set_bonus_reward(amount)

    await state.clear()

    await message.answer(
        f"✅ Бонус обновлён: {amount}⭐"
    )


# ===================== ПРОМОКОДЫ =====================

@router.callback_query(F.data == "add_promo")
async def addpromo_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    await state.set_state(AddPromo.code)

    await callback.message.answer(
        "Введите название промокода:"
    )

    await callback.answer()


@router.message(AddPromo.code)
async def addpromo_code(message: Message, state: FSMContext):
    await state.update_data(
        code=message.text.strip().upper()
    )

    await state.set_state(AddPromo.reward)

    await message.answer(
        "Введите награду в звёздах:"
    )


@router.message(AddPromo.reward)
async def addpromo_reward(message: Message, state: FSMContext):
    try:
        reward = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer(
            "Введите число. Например: 5 или 0.6"
        )
        return

    await state.update_data(reward=reward)

    await state.set_state(AddPromo.uses)

    await message.answer(
        "Введите количество использований:"
    )


@router.message(AddPromo.uses)
async def addpromo_uses(message: Message, state: FSMContext):
    try:
        uses = int(message.text)
    except ValueError:
        await message.answer(
            "Введите целое число."
        )
        return

    data = await state.get_data()

    await add_promocode(
        code=data["code"],
        reward=data["reward"],
        uses=uses
    )

    await state.clear()

    await message.answer(
        f"✅ Промокод {data['code']} создан\n\n"
        f"⭐ Награда: {data['reward']}\n"
        f"🔢 Использований: {uses}"
    )


@router.callback_query(F.data == "list_promos")
async def list_promos(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    promos = await get_all_promocodes()

    if not promos:
        await callback.answer(
            "❌ Промокодов нет",
            show_alert=True
        )
        return

    text = "🎁 Список промокодов:\n\n"

    for code, reward, uses in promos:
        text += (
            f"🔹 {code}\n"
            f"⭐ Награда: {reward}\n"
            f"🔢 Осталось использований: {uses}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data == "delete_promo")
async def delete_promo_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    promos = await get_all_promocodes()

    if not promos:
        await callback.answer(
            "❌ Промокодов нет",
            show_alert=True
        )
        return

    await callback.message.answer(
        "Выберите промокод:",
        reply_markup=delete_promos_kb(promos)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("delete_promo_"))
async def delete_promo_item(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    code = callback.data.replace(
        "delete_promo_",
        ""
    )

    await delete_promocode(code)

    await callback.message.edit_text(
        f"✅ Промокод {code} удалён"
    )

    await callback.answer()


# ===================== РАССЫЛКА =====================

@router.callback_query(F.data == "broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    await state.set_state(Broadcast.waiting_message)

    await callback.message.answer(
        "📢 Отправьте сообщение для рассылки.\n\n"
        "Поддерживается: текст, фото с подписью, видео, документ."
    )

    await callback.answer()


@router.message(Broadcast.waiting_message)
async def broadcast_send(message: Message, bot: Bot, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    await state.clear()

    users = await get_all_users()

    status = await message.answer(f"⏳ Начинаю рассылку на {len(users)} пользователей...")

    ok = 0
    fail = 0

    for user_id in users:
        try:
            await message.copy_to(user_id)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)

    await status.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: {ok}\n"
        f"❌ Ошибок: {fail}"
    )


# ===================== ИЗМЕНИТЬ ФОТО =====================

@router.callback_query(F.data == "change_photos")
async def change_photos_menu(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return

    await callback.message.answer(
        "🖼 Выберите фото для замены:",
        reply_markup=photos_kb()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("set_photo:"))
async def set_photo_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        return

    key = callback.data.split(":", 1)[1]

    if key not in PHOTO_LABELS:
        await callback.answer("Неизвестное фото", show_alert=True)
        return

    await state.set_state(ChangePhoto.waiting_photo)
    await state.update_data(photo_key=key)

    await callback.message.answer(
        f"📷 Отправьте новое фото для «{PHOTO_LABELS[key]}»:"
    )

    await callback.answer()


@router.message(ChangePhoto.waiting_photo)
async def set_photo_save(message: Message, bot: Bot, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return

    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото (не файл).")
        return

    data = await state.get_data()
    key = data["photo_key"]

    await state.clear()

    os.makedirs("images", exist_ok=True)

    path = f"images/{key}.png"
    file = await bot.get_file(message.photo[-1].file_id)
    await bot.download_file(file.file_path, destination=path)

    await message.answer(
        f"✅ Фото «{PHOTO_LABELS[key]}» обновлено!"
    )