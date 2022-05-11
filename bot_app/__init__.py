from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import Config

bot = Bot(token=Config.TOKEN, parse_mode="HTML")
storage = MemoryStorage()
db = Dispatcher(bot, storage=storage)