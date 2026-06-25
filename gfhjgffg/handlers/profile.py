@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    balance = await get_balance(callback.from_user.id)
    referrals_count = await get_referrals_count(callback.from_user.id)

    caption = (
        f"<b>Имя:</b> {callback.from_user.full_name}\n"
        f"<b>ID:</b> <code>{callback.from_user.id}</code>\n\n"
        f"<b>Баланс:</b> {balance} ⭐️\n"
        f"<b>Приглашено друзей:</b> {referrals_count}"
    )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/profile.png"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=profile_kb()
    )

    await callback.answer()