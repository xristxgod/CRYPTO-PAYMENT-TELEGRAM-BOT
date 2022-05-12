from aiogram.dispatcher.filters.state import State, StatesGroup

class StateRegistrationForm(StatesGroup):
    inviter_id = State()
    lang_id = State()