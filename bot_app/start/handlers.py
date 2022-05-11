from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from src.middlewares.__init__ import UserData
from src.models import UserModel
from . import dp, bot

@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE, state='*')
async def start(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    if not db_user.exists():
        params = message.get_full_command()
        if len(params) < 2 or not params[1].isdigit() or not await UserModel.exists(id=int(params[1])):
            return await send_message(message.chat)