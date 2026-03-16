from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='✨ Профиль', callback_data='profile'),
            InlineKeyboardButton(text='👥 Рефералы', callback_data='refs'),
        ],
        [
            InlineKeyboardButton(text='🎁 Ежедневный Бонус', callback_data='daily_bonus'),
            InlineKeyboardButton(text='🎰 Рулетка', callback_data='spin'),
        ],
        [
            InlineKeyboardButton(text='💳 Вывод', callback_data='withdraw_menu'),
            InlineKeyboardButton(text='📝 Задания', callback_data='tasks'),
        ],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_main')]]
    )


def withdraw_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='15 ⭐', callback_data='wd_15'),
            InlineKeyboardButton(text='25 ⭐', callback_data='wd_25'),
        ],
        [
            InlineKeyboardButton(text='50 ⭐', callback_data='wd_50'),
            InlineKeyboardButton(text='100 ⭐', callback_data='wd_100'),
        ],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_main')],
    ])


def botohub_wall_kb(tasks: list) -> InlineKeyboardMarkup:
    rows = []
    for i, url in enumerate(tasks, start=1):
        rows.append([InlineKeyboardButton(text=f'Канал #{i}', url=url)])
    rows.append([InlineKeyboardButton(text='✅ Я подписался', callback_data='botohub:check')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def required_subs_kb(channels: list) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f'Канал #{i}', url=row['link'])]
        for i, row in enumerate(channels, start=1)
    ]
    rows.append([InlineKeyboardButton(text='✅ Я подписался', callback_data='check_subs')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subgram_wall_kb(tasks: list) -> InlineKeyboardMarkup:
    rows = []
    for i, url in enumerate(tasks, start=1):
        rows.append([InlineKeyboardButton(text=f'Канал #{i}', url=url)])
    rows.append([InlineKeyboardButton(text='✅ Я подписался', callback_data='subgram:check')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── Admin keyboards ──────────────────────────────────────────────────────────

def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📊 Статистика', callback_data='adm:stats'),
            InlineKeyboardButton(text='💳 Pending виводи', callback_data='adm:pending'),
        ],
        [
            InlineKeyboardButton(text='📝 Задання', callback_data='adm:tasks'),
            InlineKeyboardButton(text='📢 Канали', callback_data='adm:channels'),
        ],
        [
            InlineKeyboardButton(text='⚙️ Бонус', callback_data='adm:bonus_info'),
            InlineKeyboardButton(text='👥 Юзери', callback_data='adm:users_info'),
        ],
    ])


def admin_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🔙 Назад', callback_data='adm:main')]]
    )


def admin_pending_kb(rows: list) -> InlineKeyboardMarkup:
    buttons = []
    for row in rows:
        buttons.append([
            InlineKeyboardButton(
                text=f'✅ #{row["id"]} | @{row["username"]} | {row["amount"]}⭐',
                callback_data=f'adm:confirm:{row["id"]}',
            )
        ])
    buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='adm:main')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_tasks_kb(tasks: list) -> InlineKeyboardMarkup:
    buttons = []
    for t in tasks:
        label = (t['title'] or t['link'])[:30]
        buttons.append([
            InlineKeyboardButton(text=f'🗑 {label} ({t["reward"]}⭐)', callback_data=f'adm:del_task:{t["id"]}')
        ])
    buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='adm:main')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_channels_kb(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        label = ch['link'][:40]
        buttons.append([
            InlineKeyboardButton(text=f'🗑 {label}', callback_data=f'adm:del_chan:{ch["id"]}')
        ])
    buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='adm:main')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
