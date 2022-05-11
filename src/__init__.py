import logging

from aiogram import Bot, Dispatcher

from config import Config

logging.basicConfig(level=logging.INFO)
bot = Bot(token=Config.TOKEN)
db = Dispatcher(bot)