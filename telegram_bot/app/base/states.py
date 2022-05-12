from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class JustWaitState(StatesGroup):
    wait = State()

async def update_data(state: FSMContext, **kwargs):
    """Update current state of FSM"""
    await state.update_data(**kwargs)
    return state

async def get_data(state: FSMContext, *args):
    """Return data for list of fields *args from FSM"""
    values = []
    async with state.proxy() as data:
        for key in args:
            if key in data.keys():
                values.append(data[key])
    return values if len(values) > 1 else values[0]

async def get_data_dict(state: FSMContext) -> dict:
    """Return dict from FSM"""
    async with state.proxy() as data:
        return data.as_dict()