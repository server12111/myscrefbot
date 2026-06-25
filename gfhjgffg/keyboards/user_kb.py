from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Заработать звёзды",
                    callback_data="earn"
                ),
                InlineKeyboardButton(
                    text="Вывести звёзды",
                    callback_data="withdraw"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Мой профиль",
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text="Бонус",
                    callback_data="bonus"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Промокод",
                    callback_data="promo"
                ),
                InlineKeyboardButton(
                    text="Топ рефералов",
                    callback_data="top"
                )
            ]
        ]
    )


def earn_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )


def profile_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Пригласить друзей",
                    callback_data="earn"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )


def withdraw_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="15⭐",
                    callback_data="withdraw_15"
                ),
                InlineKeyboardButton(
                    text="25⭐",
                    callback_data="withdraw_25"
                )
            ],
            [
                InlineKeyboardButton(
                    text="50⭐",
                    callback_data="withdraw_50"
                ),
                InlineKeyboardButton(
                    text="100⭐",
                    callback_data="withdraw_100"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )


def sponsors_kb(channels: list) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=f"Спонсор {i}", url=url)
        for i, (_, url) in enumerate(channels, start=1)
    ]

    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

    keyboard.append([
        InlineKeyboardButton(
            text="✅ Я подписался",
            callback_data="check_subs"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def promo_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )


def back_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_menu"
                )
            ]
        ]
    )