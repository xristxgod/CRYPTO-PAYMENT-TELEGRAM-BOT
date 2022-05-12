from aiogram.dispatcher.filters.state import State, StatesGroup

class UserBroadcastState(StatesGroup):
    text = State()
    agree = State()