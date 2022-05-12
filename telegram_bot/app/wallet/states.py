from aiogram.dispatcher.filters.state import State, StatesGroup

class PayState(StatesGroup):
    value = State()
    address = State()
    agree = State()