from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.utils.lang_selector import lang_selector
from config import Config

bot = Bot(token=Config.TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def send_message(user_id: int, code: str, lang_id: int, keyboard=None):
    return await bot.send_message(
        user_id,
        await lang_selector.say(code, lang_id),
        reply_markup=keyboard, disable_web_page_preview=True
    )

async def send_msg_text(user_id: int, text: str, keyboard=None):
    return await bot.send_message(user_id, text, reply_markup=keyboard, disable_web_page_preview=True)