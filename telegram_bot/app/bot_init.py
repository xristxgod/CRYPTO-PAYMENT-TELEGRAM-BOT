from src.utils.lang_selector import lang_selector
from config import Config
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from src.middlewares.user_database.check_user import UserData
from app.base.states import get_data, update_data, get_data_dict

bot = Bot(Config.TOKEN, parse_mode='HTML')

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