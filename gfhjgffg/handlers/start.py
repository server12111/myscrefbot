from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile

from database.sponsors import get_sponsors
from database.settings import get_ref_reward
from database.integrations import (
    get_tgrass_offers,
    check_tgrass_subscribed,
    get_botohub_tasks,
    check_botohub_completed,
    extract_channel_name
)

from database.users import (
    add_user,
    is_verified,
    set_verified,
    remove_verified,
    get_referrer,
    add_balance,
    get_balance,
    is_rewarded,
    set_rewarded,
    get_referrals_count
)

from keyboards.user_kb import (
    sponsors_kb,
    main_menu,
    profile_kb
)

router = Router()


async def build_all_channels(user_id: int, is_premium: bool = False) -> list:
    """Собирает всех спонсоров (БД + tgrass + botohub) в единый список (name, url)."""
    db_sponsors = await get_sponsors()
    tgrass_offers = await get_tgrass_offers(user_id, is_premium)
    botohub_tasks, botohub_completed = await get_botohub_tasks(user_id)

    all_channels = []

    for s in db_sponsors:
        all_channels.append((s[3], s[2]))  # (title, link)

    for offer in tgrass_offers:
        name = offer.get("name") or "Канал"
        link = offer.get("link", "")
        if link:
            all_channels.append((name, link))

    if not botohub_completed:
        for url in botohub_tasks:
            name = extract_channel_name(str(url))
            all_channels.append((name, url))

    return all_channels


# ===================== CHECK SUBSCRIPTIONS =====================

async def check_subscriptions(bot: Bot, user_id: int, is_premium: bool = False) -> bool:
    db_sponsors = await get_sponsors()

    for sponsor in db_sponsors:
        try:
            member = await bot.get_chat_member(
                chat_id=sponsor[1],
                user_id=user_id
            )
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            return False

    if not await check_tgrass_subscribed(user_id, is_premium):
        return False

    if not await check_botohub_completed(user_id):
        return False

    return True


# ===================== START =====================

@router.message(CommandStart())
async def start(message: Message, bot: Bot, command: CommandObject):
    referrer_id = None

    if command.args:
        try:
            referrer_id = int(command.args)
            if referrer_id == message.from_user.id:
                referrer_id = None
        except ValueError:
            pass

    await add_user(message.from_user.id, referrer_id)

    if referrer_id:
        already_rewarded = await is_rewarded(message.from_user.id)

        if not already_rewarded:
            username = message.from_user.username
            username = f"@{username}" if username else message.from_user.full_name

            await bot.send_message(
                referrer_id,
                f"👤 Ваш друг {username} зашёл по вашей ссылке!\n\n"
                "Вы получите награду после того, как он подпишется на спонсоров."
            )

    is_premium = bool(getattr(message.from_user, "is_premium", False))
    verified = await is_verified(message.from_user.id)

    if verified:
        subscribed = await check_subscriptions(bot, message.from_user.id, is_premium)

        if subscribed:
            await message.answer_photo(
                photo=FSInputFile("images/menu.png"),
                caption="✨ Добро пожаловать!",
                reply_markup=main_menu()
            )
            return

        await remove_verified(message.from_user.id)

    all_channels = await build_all_channels(message.from_user.id, is_premium)

    if not all_channels:
        await message.answer_photo(
            photo=FSInputFile("images/menu.png"),
            caption="✨ Добро пожаловать!",
            reply_markup=main_menu()
        )
        return

    await message.answer_photo(
        photo=FSInputFile("images/sponsors.png"),
        caption=(
            "🎁 Чтобы пользоваться ботом,\n"
            "подпишитесь на все каналы ниже."
        ),
        reply_markup=sponsors_kb(all_channels)
    )


# ===================== CHECK SUBS =====================

@router.callback_query(F.data == "check_subs")
async def check_subs(callback: CallbackQuery, bot: Bot):
    is_premium = bool(getattr(callback.from_user, "is_premium", False))

    subscribed = await check_subscriptions(bot, callback.from_user.id, is_premium)

    if not subscribed:
        await callback.answer(
            text="❌ Вы подписались не на все каналы.",
            show_alert=True
        )
        return

    was_verified = await is_verified(callback.from_user.id)

    await set_verified(callback.from_user.id)

    if not was_verified:
        if await is_rewarded(callback.from_user.id):
            await callback.message.delete()

            await callback.message.answer_photo(
                photo=FSInputFile("images/menu.png"),
                caption="✨ Добро пожаловать!",
                reply_markup=main_menu()
            )

            await callback.answer()
            return

        referrer_id = await get_referrer(callback.from_user.id)

        if referrer_id:
            reward = await get_ref_reward()

            username = callback.from_user.username
            username = f"@{username}" if username else callback.from_user.full_name

            await add_balance(referrer_id, reward)
            balance = await get_balance(referrer_id)

            await bot.send_message(
                referrer_id,
                f"💰 На ваш баланс было зачислено "
                f"{reward}⭐️ за приглашение {username}\n\n"
                f"Ваш баланс: {balance}⭐️"
            )

            await set_rewarded(callback.from_user.id)

    await callback.message.delete()

    await callback.message.answer_photo(
        photo=FSInputFile("images/menu.png"),
        caption="✨ Добро пожаловать!",
        reply_markup=main_menu()
    )

    await callback.answer()


# ===================== PROFILE =====================

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    balance = await get_balance(callback.from_user.id)
    referrals_count = await get_referrals_count(callback.from_user.id)

    caption = (
        f"👤 <b>Имя:</b> {callback.from_user.full_name}\n"
        f"🆔 <b>ID:</b> <code>{callback.from_user.id}</code>\n\n"
        f"💰 <b>Баланс:</b> {balance} ⭐️\n"
        f"👥 <b>Приглашено друзей:</b> {referrals_count}"
    )

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/profile.png"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=profile_kb()
    )

    await callback.answer()


# ===================== BACK MENU =====================

@router.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/menu.png"),
        caption="✨ Добро пожаловать!",
        reply_markup=main_menu()
    )

    await callback.answer()
