from aiogram import types

from app.start.callbacks import choose_lang_cb
from src.models import Lang

async def lang_choose_keyboard():
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for lang in await Lang.all():
        keyboard.add(types.InlineKeyboardButton(lang.name, callback_data=choose_lang_cb.new(id=lang.id)))
    return keyboard