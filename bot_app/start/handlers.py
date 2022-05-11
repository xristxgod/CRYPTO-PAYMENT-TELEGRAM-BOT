from aiogram import types

from . import dp, bot

@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE, state='*')
async def start(message: types.Message, state: FS):
    if message.chat.type == "private":
        pass