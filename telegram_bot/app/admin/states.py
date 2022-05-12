from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminUtilsState(StatesGroup):
    wait = State()