from aiogram import types

from app.extra.callbacks import extra_cb, Action
from src.middlewares.user_database.check_user import UserData
from src.utils.lang_selector import lang_selector
from config import Config

async def extra_menu_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('main_extra_promo', db_user.lang_id),
        callback_data=extra_cb.new(action=Action.promo)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('main_extra_channel', db_user.lang_id), url='https://t.me/smartex_official'
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('main_extra_support', db_user.lang_id), url='https://t.me/smartex_support'
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('main_extra_change_lang', db_user.lang_id),
        callback_data=extra_cb.new(action=Action.edit_lang)
    ))
    if db_user.id in Config.ADMIN_IDS:
        keyboard.add(types.InlineKeyboardButton(
            await lang_selector.say('main_extra_admin', db_user.lang_id),
            callback_data=extra_cb.new(action=Action.open_admin)
        ))
    return keyboard

async def promo_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('extra_prezent_ru', db_user.lang_id), url='https://t.me/smartex_official/11'
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('extra_prezent_en', db_user.lang_id), url='https://t.me/smartex_official/12'
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('extra_video_ru', db_user.lang_id), url='https://t.me/smartex_official/15'
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('extra_video_en', db_user.lang_id), url='https://t.me/smartex_official/16'
    ))
    return keyboard