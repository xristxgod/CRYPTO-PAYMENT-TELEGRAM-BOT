from aiogram import types

from app.base.callbacks import admin_cb, Action
from app.base.callbacks import close_cb, BaseAction
from src.utils.lang_selector import lang_selector
from src.middlewares.user_database.check_user import UserData

async def add_close_btn(keyboard, lang_id: int):
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data=close_cb.new(action=BaseAction.close)))
    return keyboard

async def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*[
        types.InlineKeyboardButton(
            text, callback_data=admin_cb.new(action=action)
        )
        for text, action in [
            ('Пользователи', Action.excel_users),
            ('Транзакции', Action.excel_transactions),
            ('Статистика программ', Action.excel_programmes),
            ('Рассылка', Action.broadcast),
        ]
    ])
    return keyboard

async def main_keyboard(db_user: UserData):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*[
        types.InlineKeyboardButton(await lang_selector.say(code, db_user.lang_id))
        for code in ['btn_main_wallet', 'btn_main_programmes', 'btn_main_struct', 'btn_main_extra']
    ])
    return keyboard

async def url_keyboard(title: str, url: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=title, url=url))
    return keyboard