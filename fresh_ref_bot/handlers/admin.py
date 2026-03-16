import asyncio
from datetime import datetime

from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject

from config import ADMIN_IDS
from database import get_db
from keyboards import admin_main_kb, admin_back_kb, admin_pending_kb, admin_tasks_kb, admin_channels_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command('admin'))
async def admin_help(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        '👑 <b>Admin панель</b>',
        reply_markup=admin_main_kb(),
        parse_mode='HTML',
    )


# ─── Admin button callbacks ───────────────────────────────────────────────────

@router.callback_query(F.data == 'adm:main')
async def adm_main(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    try:
        await callback.message.edit_text('👑 <b>Admin панель</b>', reply_markup=admin_main_kb(), parse_mode='HTML')
    except Exception:
        await callback.message.answer('👑 <b>Admin панель</b>', reply_markup=admin_main_kb(), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data == 'adm:stats')
async def adm_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    with get_db() as conn:
        users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        banned = conn.execute('SELECT COUNT(*) FROM users WHERE banned = 1').fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM withdraw_requests WHERE status = 'pending'").fetchone()[0]
        total_balance = conn.execute('SELECT COALESCE(SUM(balance), 0) FROM users').fetchone()[0]
    text = (
        f'📊 <b>Статистика</b>\n\n'
        f'👥 Пользователей: {users}\n'
        f'⛔️ Забанено: {banned}\n'
        f'⏳ Pending виводів: {pending}\n'
        f'💰 Сума балансів: {float(total_balance):.2f}⭐'
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data == 'adm:pending')
async def adm_pending(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, user_id, username, amount, created_at FROM withdraw_requests WHERE status = 'pending' ORDER BY id DESC LIMIT 10"
        ).fetchall()
    if not rows:
        try:
            await callback.message.edit_text('Pending заявок немає.', reply_markup=admin_back_kb())
        except Exception:
            await callback.message.answer('Pending заявок немає.', reply_markup=admin_back_kb())
        await callback.answer()
        return
    text = '💳 <b>Pending виводи</b>\nНатисни кнопку щоб підтвердити:'
    try:
        await callback.message.edit_text(text, reply_markup=admin_pending_kb(rows), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_pending_kb(rows), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data.startswith('adm:confirm:'))
async def adm_confirm(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    req_id = int(callback.data.split(':')[2])
    with get_db() as conn:
        req = conn.execute('SELECT * FROM withdraw_requests WHERE id = ?', (req_id,)).fetchone()
        if not req:
            await callback.answer('❌ Заявку не знайдено.', show_alert=True)
            return
        if req['status'] != 'pending':
            await callback.answer('❌ Вже оброблено.', show_alert=True)
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            "UPDATE withdraw_requests SET status = 'completed', processed_at = ? WHERE id = ?",
            (now, req_id),
        )
        log_chat = int(conn.execute("SELECT value FROM config WHERE key = 'log_chat_id'").fetchone()[0])
        conn.commit()

    try:
        await callback.bot.send_message(
            req['user_id'],
            f'✅ <b>Ваш вывод выполнен!</b>\nЗаявка: #{req_id}\nСумма: {req["amount"]}⭐',
            parse_mode='HTML',
        )
    except Exception:
        pass

    if log_chat != 0:
        try:
            await callback.bot.send_message(
                log_chat,
                f'✅ <b>Заявка выполнена</b>\nНомер: #{req_id}\n@{req["username"]} (ID {req["user_id"]})\nСумма: {req["amount"]}⭐',
                parse_mode='HTML',
            )
        except Exception:
            pass

    await callback.answer(f'✅ Заявка #{req_id} виконана!')
    # Refresh pending list
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, user_id, username, amount, created_at FROM withdraw_requests WHERE status = 'pending' ORDER BY id DESC LIMIT 10"
        ).fetchall()
    if not rows:
        try:
            await callback.message.edit_text('Pending заявок немає.', reply_markup=admin_back_kb())
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_reply_markup(reply_markup=admin_pending_kb(rows))
        except Exception:
            pass


@router.callback_query(F.data == 'adm:tasks')
async def adm_tasks(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    with get_db() as conn:
        tasks = conn.execute('SELECT id, title, link, reward FROM tasks WHERE is_active = 1').fetchall()
    if not tasks:
        try:
            await callback.message.edit_text('Активних завдань немає.', reply_markup=admin_back_kb())
        except Exception:
            await callback.message.answer('Активних завдань немає.', reply_markup=admin_back_kb())
        await callback.answer()
        return
    text = '📝 <b>Активні завдання</b>\nНатисни кнопку щоб видалити:'
    try:
        await callback.message.edit_text(text, reply_markup=admin_tasks_kb(tasks), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_tasks_kb(tasks), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data.startswith('adm:del_task:'))
async def adm_del_task(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    task_id = int(callback.data.split(':')[2])
    with get_db() as conn:
        conn.execute('UPDATE tasks SET is_active = 0 WHERE id = ?', (task_id,))
        conn.commit()
    await callback.answer('🗑 Завдання видалено!')
    # Refresh
    with get_db() as conn:
        tasks = conn.execute('SELECT id, title, link, reward FROM tasks WHERE is_active = 1').fetchall()
    if not tasks:
        try:
            await callback.message.edit_text('Активних завдань немає.', reply_markup=admin_back_kb())
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_reply_markup(reply_markup=admin_tasks_kb(tasks))
        except Exception:
            pass


@router.callback_query(F.data == 'adm:channels')
async def adm_channels(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    with get_db() as conn:
        rows = conn.execute('SELECT rowid AS id, link FROM required_channels').fetchall()
    if not rows:
        try:
            await callback.message.edit_text('Обов\'язкових каналів немає.', reply_markup=admin_back_kb())
        except Exception:
            await callback.message.answer('Обов\'язкових каналів немає.', reply_markup=admin_back_kb())
        await callback.answer()
        return
    text = '📢 <b>Обов\'язкові канали</b>\nНатисни кнопку щоб видалити:'
    try:
        await callback.message.edit_text(text, reply_markup=admin_channels_kb(rows), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_channels_kb(rows), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data.startswith('adm:del_chan:'))
async def adm_del_chan(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rowid = int(callback.data.split(':')[2])
    with get_db() as conn:
        conn.execute('DELETE FROM required_channels WHERE rowid = ?', (rowid,))
        conn.commit()
    await callback.answer('🗑 Канал видалено!')
    # Refresh
    with get_db() as conn:
        rows = conn.execute('SELECT rowid AS id, link FROM required_channels').fetchall()
    if not rows:
        try:
            await callback.message.edit_text('Обов\'язкових каналів немає.', reply_markup=admin_back_kb())
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_reply_markup(reply_markup=admin_channels_kb(rows))
        except Exception:
            pass


@router.callback_query(F.data == 'adm:bonus_info')
async def adm_bonus_info(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    with get_db() as conn:
        b_min = conn.execute("SELECT value FROM config WHERE key = 'bonus_min'").fetchone()[0]
        b_max = conn.execute("SELECT value FROM config WHERE key = 'bonus_max'").fetchone()[0]
    text = (
        f'⚙️ <b>Поточний діапазон бонусу</b>\n\n'
        f'Від: {b_min}⭐\n'
        f'До: {b_max}⭐\n\n'
        f'Щоб змінити: /setbonus [мін] [макс]'
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    await callback.answer()


@router.callback_query(F.data == 'adm:users_info')
async def adm_users_info(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    text = (
        '👥 <b>Управління юзерами</b>\n\n'
        '/ban [id] — забанити\n'
        '/unban [id] — розбанити\n'
        '/star [id] [сума] — видати зірки'
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    except Exception:
        await callback.message.answer(text, reply_markup=admin_back_kb(), parse_mode='HTML')
    await callback.answer()


@router.message(Command('promo'))
async def add_promo(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    parts = (command.args or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /promo код сумма')
        return
    code = parts[0]
    try:
        reward = float(parts[1])
    except ValueError:
        await message.answer('Сумма должна быть числом.')
        return
    with get_db() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO promocodes (code, reward, is_active) VALUES (?, ?, 1)', (code, reward)
        )
        conn.commit()
    await message.answer(f'✅ Промокод <b>{code}</b> на {reward}⭐ создан!', parse_mode='HTML')


@router.message(Command('star'))
async def give_stars(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    parts = (command.args or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /star [id] [сумма]')
        return
    try:
        uid, reward = int(parts[0]), float(parts[1])
    except ValueError:
        await message.answer('ID и сумма должны быть числами.')
        return
    with get_db() as conn:
        conn.execute(
            'UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE user_id = ?',
            (reward, reward, uid),
        )
        conn.commit()
    await message.answer(f'✅ Выдано {reward}⭐ пользователю {uid}')
    try:
        await message.bot.send_message(uid, f'🎁 Администратор выдал вам <b>{reward} ⭐</b>!', parse_mode='HTML')
    except Exception:
        pass


@router.message(Command('task'))
async def add_task(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    parts = (command.args or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /task [ссылка] [сумма]')
        return
    link = parts[0]
    try:
        reward = float(parts[1])
    except ValueError:
        await message.answer('Сумма должна быть числом.')
        return
    with get_db() as conn:
        conn.execute('INSERT INTO tasks (link, reward) VALUES (?, ?)', (link, reward))
        conn.commit()
    await message.answer(f'✅ Задание добавлено: {link} ({reward}⭐)')


@router.message(Command('addchan'))
async def add_channel(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    link = (command.args or '').strip()
    if not link:
        await message.answer('Формат: /addchan ссылка')
        return
    with get_db() as conn:
        conn.execute('INSERT OR IGNORE INTO required_channels (link) VALUES (?)', (link,))
        conn.commit()
    await message.answer('✅ Канал добавлен.')


@router.message(Command('delchan'))
async def del_channel(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    link = (command.args or '').strip()
    if not link:
        await message.answer('Формат: /delchan ссылка')
        return
    with get_db() as conn:
        conn.execute('DELETE FROM required_channels WHERE link = ?', (link,))
        conn.commit()
    await message.answer('✅ Канал удален.')


@router.message(Command('text'))
async def broadcast(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    txt = (command.args or '').strip()
    if not txt:
        await message.answer('Формат: /text [сообщение]')
        return
    with get_db() as conn:
        users = conn.execute('SELECT user_id FROM users WHERE banned = 0').fetchall()
    await message.answer('⏳ Рассылка начата...')
    sent = 0
    for row in users:
        try:
            await message.bot.send_message(row['user_id'], txt, parse_mode='HTML')
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f'✅ Готово. Доставлено: {sent}')


@router.message(Command('setbonus'))
async def set_bonus(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    parts = (command.args or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /setbonus мин макс')
        return
    try:
        b_min, b_max = float(parts[0]), float(parts[1])
    except ValueError:
        await message.answer('Числа, пожалуйста.')
        return
    if b_min <= 0 or b_max <= 0 or b_min > b_max:
        await message.answer('Некорректный диапазон.')
        return
    with get_db() as conn:
        conn.execute("UPDATE config SET value = ? WHERE key = 'bonus_min'", (str(b_min),))
        conn.execute("UPDATE config SET value = ? WHERE key = 'bonus_max'", (str(b_max),))
        conn.commit()
    await message.answer(f'✅ Бонус: от {b_min} до {b_max}⭐')


@router.message(Command('ban'))
async def ban_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args or not command.args.isdigit():
        await message.answer('Формат: /ban [id]')
        return
    with get_db() as conn:
        conn.execute('UPDATE users SET banned = 1 WHERE user_id = ?', (int(command.args),))
        conn.commit()
    await message.answer(f'⛔️ Забанен: {command.args}')


@router.message(Command('unban'))
async def unban_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args or not command.args.isdigit():
        await message.answer('Формат: /unban [id]')
        return
    with get_db() as conn:
        conn.execute('UPDATE users SET banned = 0 WHERE user_id = ?', (int(command.args),))
        conn.commit()
    await message.answer(f'✅ Розбанений: {command.args}')


@router.message(Command('vv'))
async def set_log(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    if message.chat.type == 'private':
        await message.answer(
            '📢 Щоб налаштувати лог-канал:\n'
            '1. Додайте бота в канал як адміністратора\n'
            '2. Напишіть /vv в тому каналі'
        )
        return
    with get_db() as conn:
        conn.execute("UPDATE config SET value = ? WHERE key = 'log_chat_id'", (str(message.chat.id),))
        conn.commit()
    await message.answer(f'✅ Лог-канал встановлено: {message.chat.title} (ID {message.chat.id})')


@router.channel_post(Command('vv'))
async def channel_vv(post: types.Message):
    with get_db() as conn:
        conn.execute("UPDATE config SET value = ? WHERE key = 'log_chat_id'", (str(post.chat.id),))
        conn.commit()
    try:
        await post.bot.send_message(
            post.chat.id,
            f'✅ Лог-канал встановлено: {post.chat.title} (ID {post.chat.id})',
        )
    except Exception:
        pass


@router.message(Command('checklog'))
async def check_log(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    with get_db() as conn:
        val = conn.execute("SELECT value FROM config WHERE key = 'log_chat_id'").fetchone()[0]
    if val and val != '0':
        await message.answer(f'📢 Поточний лог-канал: ID {val}')
    else:
        await message.answer('📢 Лог-канал не налаштований. Використай /vv в каналі.')


@router.message(Command('t'))
async def confirm_withdraw(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args or not command.args.isdigit():
        await message.answer('Формат: /t [номер заявки]')
        return
    req_id = int(command.args)

    with get_db() as conn:
        req = conn.execute('SELECT * FROM withdraw_requests WHERE id = ?', (req_id,)).fetchone()
        if not req:
            await message.answer('❌ Заявка не найдена.')
            return
        if req['status'] != 'pending':
            await message.answer(f"❌ Уже обработана (статус: {req['status']}).")
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            "UPDATE withdraw_requests SET status = 'completed', processed_at = ? WHERE id = ?",
            (now, req_id),
        )
        log_chat = int(conn.execute("SELECT value FROM config WHERE key = 'log_chat_id'").fetchone()[0])
        conn.commit()

    try:
        await message.bot.send_message(
            req['user_id'],
            f'✅ <b>Ваш вывод выполнен!</b>\nЗаявка: #{req_id}\nСумма: {req["amount"]}⭐',
            parse_mode='HTML',
        )
    except Exception:
        pass

    if log_chat != 0:
        try:
            await message.bot.send_message(
                log_chat,
                f'✅ <b>Заявка выполнена</b>\nНомер: #{req_id}\n@{req["username"]} (ID {req["user_id"]})\nСумма: {req["amount"]}⭐',
                parse_mode='HTML',
            )
        except Exception:
            pass

    await message.answer(f'✅ Заявка #{req_id} виконана.')


@router.message(Command('pending'))
async def pending_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, user_id, username, amount, created_at FROM withdraw_requests WHERE status = 'pending' ORDER BY id DESC LIMIT 10"
        ).fetchall()
    if not rows:
        await message.answer('Pending заявок нет.')
        return
    lines = ['<b>Pending заявки:</b>']
    for row in rows:
        lines.append(f"#{row['id']} | @{row['username']} | {row['amount']}⭐ | {row['created_at']}")
    await message.answer('\n'.join(lines), parse_mode='HTML')


@router.message(Command('stats'))
async def stats_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    with get_db() as conn:
        users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        banned = conn.execute('SELECT COUNT(*) FROM users WHERE banned = 1').fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM withdraw_requests WHERE status = 'pending'").fetchone()[0]
        total_balance = conn.execute('SELECT COALESCE(SUM(balance), 0) FROM users').fetchone()[0]
    await message.answer(
        f'👥 Пользователей: {users}\n'
        f'⛔️ Забанено: {banned}\n'
        f'⏳ Pending выводов: {pending}\n'
        f'💰 Сумма балансов: {float(total_balance):.2f}⭐'
    )
