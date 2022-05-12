from aiogram import types

from app.programmes.callbacks import programmes_cb, Action
from src.middlewares.user_database.check_user import UserData
from src.utils.lang_selector import lang_selector
from src.models import Table, Purchase, Queue

async def programmes_menu_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = []
    for program in await Table.all():
        if await Queue.exists(user_id=db_user.db_id, table_id=program.id):
            status = '✅'
        elif await Purchase.exists(user_id=db_user.db_id, table_id=program.id):
            status = '❗'
        elif program.is_active:
            status = '🟠'
        else:
            status = '⏰'

        btns.append(types.InlineKeyboardButton(
            f'{status} {program.name}', callback_data=programmes_cb.new(id=program.id, action=Action.choose)
        ))
    keyboard.add(*btns)
    return keyboard

async def program_buy_detail_keyboard(table: Table, db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*[
        types.InlineKeyboardButton(
            await lang_selector.format('programmes_btn_buy', db_user.lang_id, cost="%.4f" % table.cost),
            callback_data=programmes_cb.new(id=table.id, action=Action.buy)
        ),
        types.InlineKeyboardButton(
            await lang_selector.format('programmes_btn_buy_with_queue', db_user.lang_id, cost="%.4f" % (table.cost * 2)),
            callback_data=programmes_cb.new(id=table.id, action=Action.buy_with_qualification)
        ),
        types.InlineKeyboardButton(
            await lang_selector.say('programmes_btn_buy_back', db_user.lang_id),
            callback_data=programmes_cb.new(id=table.id, action=Action.back)
        )
    ])
    return keyboard

async def program_detail_keyboard(table: Table, db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    if not await Queue.exists(user_id=db_user.db_id, table_id=table.id):
        keyboard.add(types.InlineKeyboardButton(
            await lang_selector.format('programmes_btn_buy_queue', db_user.lang_id, cost="%.4f" % table.cost),
            callback_data=programmes_cb.new(id=table.id, action=Action.buy_qualification_only)
        ))
    keyboard.add(*[
        types.InlineKeyboardButton(
            await lang_selector.format('programmes_btn_queue', db_user.lang_id, name=table.name),
            callback_data=programmes_cb.new(id=table.id, action=Action.show_queue)
        ),
        types.InlineKeyboardButton(
            await lang_selector.say('programmes_btn_download', db_user.lang_id),
            callback_data=programmes_cb.new(id=table.id, action=Action.download_stats)
        ),
    ])
    return keyboard

async def program_buy_agree_keyboard(table: Table, db_user: UserData, is_qual=False, hide=False):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    if not hide:
        keyboard.add(types.InlineKeyboardButton(
            await lang_selector.format(
                'programmes_btn_buy_with_queue' if is_qual else 'programmes_btn_buy',
                db_user.lang_id,
                cost="%.4f" % (table.cost * 2 if is_qual else table.cost)
            ),
            callback_data=programmes_cb.new(
                id=table.id, action=Action.buy_with_qualification_agree if is_qual else Action.buy_agree
            )
        ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('programmes_btn_buy_revoke', db_user.lang_id),
        callback_data=programmes_cb.new(id=table.id, action=Action.revoke)
    ))
    return keyboard

async def program_buy_qual_only_agree_keyboard(table: Table, db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.format('programmes_btn_buy_queue', db_user.lang_id, cost="%.4f" % table.cost),
        callback_data=programmes_cb.new(id=table.id, action=Action.buy_qualification_only_agree)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('programmes_btn_buy_revoke', db_user.lang_id),
        callback_data=programmes_cb.new(id=table.id, action=Action.revoke)
    ))
    return keyboard