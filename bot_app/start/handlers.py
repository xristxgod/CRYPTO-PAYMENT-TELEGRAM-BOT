from aiogram.types import Message

from . import dp, bot

@dp.message_handler(commands=["start"])
async def start(message: Message):
    if message.chat.type == "private":
        pass