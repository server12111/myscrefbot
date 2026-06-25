from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

PHOTO_LABELS = {
    "menu":     "🏠 Главное меню",
    "sponsors": "📢 Спонсоры",
    "profile":  "👤 Профиль",
    "referral": "🔗 Рефералы",
    "withdraw": "💸 Вывод",
}


def admin_panel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить спонсора",  callback_data="add_sponsor"),
                InlineKeyboardButton(text="📋 Список спонсоров",   callback_data="list_sponsors"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить спонсора",   callback_data="delete_sponsor"),
            ],
            [
                InlineKeyboardButton(text="⭐ Изменить награду",   callback_data="change_ref_reward"),
                InlineKeyboardButton(text="🎁 Изменить бонус",     callback_data="change_bonus_reward"),
            ],
            [
                InlineKeyboardButton(text="➕ Создать промокод",   callback_data="add_promo"),
                InlineKeyboardButton(text="📋 Список промокодов",  callback_data="list_promos"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить промокод",   callback_data="delete_promo"),
            ],
            [
                InlineKeyboardButton(text="📢 Рассылка",           callback_data="broadcast"),
                InlineKeyboardButton(text="🖼 Изменить фото",      callback_data="change_photos"),
            ],
        ]
    )


def photos_kb():
    keyboard = [
        [InlineKeyboardButton(text=label, callback_data=f"set_photo:{key}")]
        for key, label in PHOTO_LABELS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def delete_sponsors_kb(sponsors):
    keyboard = []
    for sponsor in sponsors:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {sponsor[3]}",
                callback_data=f"delete_sponsor_{sponsor[0]}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def delete_promos_kb(promos):
    keyboard = []
    for promo in promos:
        code = promo[0]
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {code}",
                callback_data=f"delete_promo_{code}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
