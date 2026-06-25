from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

from database.users import add_balance
from database.promocodes import activate_promocode

from keyboards.user_kb import promo_kb

router = Router()


class PromoState(StatesGroup):
    waiting_code = State()


@router.callback_query(F.data == "promo")
async def promo(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(
        photo=FSInputFile("images/promo.png"),
        caption="Введите промокод:",
        reply_markup=promo_kb()
    )

    await state.set_state(PromoState.waiting_code)

    await callback.answer()


@router.message(PromoState.waiting_code, F.text)
async def activate(message: Message, state: FSMContext):
    # Если пользователь отправил команду, выходим из режима ввода промокода
    if message.text.startswith("/"):
        await state.clear()
        return

    code = message.text.strip().upper()

    success, reward = await activate_promocode(
        message.from_user.id,
        code
    )

    if not success:
        await message.answer(
            "❌ Промокод недействителен или закончились использования.",
            reply_markup=promo_kb()
        )

        await state.clear()
        return

    await add_balance(message.from_user.id, reward)

    await message.answer(
        f"✅ Промокод успешно активирован!\n"
        f"Вам начислено {reward}⭐",
        reply_markup=promo_kb()
    )

    await state.clear()