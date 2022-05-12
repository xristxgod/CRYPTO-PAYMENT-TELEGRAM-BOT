from aiogram.dispatcher.filters.state import State, StatesGroup

class EditDataForm(StatesGroup):
    lang_id = State()