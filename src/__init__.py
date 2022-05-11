from aiogram import Bot, Dispatcher

from config import Config

bot = Bot(token=Config.TOKEN)
db = Dispatcher(bot)