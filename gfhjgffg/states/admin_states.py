from aiogram.fsm.state import State, StatesGroup


class AddSponsor(StatesGroup):
    channel_id = State()
    channel_link = State()
    title = State()


class ChangeReward(StatesGroup):
    amount = State()


class ChangeBonus(StatesGroup):
    amount = State()


class Broadcast(StatesGroup):
    waiting_message = State()


class ChangePhoto(StatesGroup):
    waiting_photo = State()