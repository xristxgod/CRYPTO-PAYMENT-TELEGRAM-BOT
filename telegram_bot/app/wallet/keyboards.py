import math

from aiogram import types
from tortoise.expressions import Q

from app.wallet.callbacks import wallet_cb, Action, profit_list_cb, purchases_list_cb
from src.middlewares.user_database.check_user import UserData
from src.utils.lang_selector import lang_selector
from src.models import Transaction, Purchase, TransactionType, TransactionStatus, Table

async def is_unfreeze(user_id: int):
    return all([
        await Purchase.exists(user_id=user_id, table_id=table.id)
        for table in await Table.all()
    ])

async def wallet_menu_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('wallet_add_money', db_user.lang_id),
        callback_data=wallet_cb.new(action=Action.add_money)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('wallet_withdraw', db_user.lang_id),
        callback_data=wallet_cb.new(action=Action.withdraw)
    ))
    keyboard.add(
        types.InlineKeyboardButton(
            await lang_selector.say('wallet_my_buy', db_user.lang_id),
            callback_data=wallet_cb.new(action=Action.my_buy)
        ),
        types.InlineKeyboardButton(
            await lang_selector.say('wallet_profit', db_user.lang_id),
            callback_data=wallet_cb.new(action=Action.my_profit)
        ),
    )
    if await is_unfreeze(db_user.db_id):
        keyboard.add(types.InlineKeyboardButton(
            await lang_selector.say('wallet_unfreeze', db_user.lang_id),
            callback_data=wallet_cb.new(action=Action.unfreeze)
        ))
    return keyboard

async def withdraw_agree_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('wallet_withdraw_accept', db_user.lang_id),
        callback_data=wallet_cb.new(action=Action.withdraw_agree)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('wallet_withdraw_revoke', db_user.lang_id),
        callback_data=wallet_cb.new(action=Action.withdraw_revoke)
    ))
    return keyboard

async def something_list_keyboard(db_user: UserData, is_tx: bool, page: int = 0):
    on_page = 6

    if is_tx:
        filters = [
            Q(user_id=db_user.db_id),
            Q(status=TransactionStatus.success),
            Q(type=TransactionType.referral)
            | Q(type=TransactionType.to_user_from_queue)
            | Q(type=TransactionType.to_user_for_buy_table)
            | Q(type=TransactionType.to_frozen)
        ]
        records = await Transaction.filter(
            *filters
        ).prefetch_related('user').order_by('updated_at').offset(page * on_page).limit(on_page + 1)

        count_all = await Transaction.filter(*filters).count()
        cb = profit_list_cb
    else:
        records = await Purchase.filter(
            user_id=db_user.db_id
        ).prefetch_related('user', 'table').order_by('created_at').offset(page * on_page).limit(on_page + 1)
        count_all = await Purchase.filter(user_id=db_user.db_id).count()
        cb = purchases_list_cb

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for record in records[:on_page]:
        if is_tx:
            text = f'{"%.4f" % record.value} BNB ({record.updated_at.strftime("%Y-%m-%d %H:%M:%S")})'
        else:
            text = f'{record.table.name}'
        keyboard.add(types.InlineKeyboardButton(
            text, callback_data=cb.new(id=record.id, page=page, action=Action.choose)
        ))

    btns = []
    if page > 0:
        btns.append(types.InlineKeyboardButton(
            '<', callback_data=cb.new(id=0, action=Action.edit_page, page=page - 1)
        ))
    btns.append(types.InlineKeyboardButton(
        f'{page + 1}/{math.ceil(count_all / on_page)}',
        callback_data=cb.new(id=0, action=Action.nothing, page=page)
    ))
    if len(records) > on_page:
        btns.append(types.InlineKeyboardButton(
            '>', callback_data=cb.new(id=0, action=Action.edit_page, page=page + 1)
        ))
    keyboard.add(*btns)
    return keyboard

async def just_back_keyboard(db_user: UserData, cb, page: int):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_send_to_partners_btn_back', db_user.lang_id),
        callback_data=cb.new(id=0, page=page, action=Action.back)
    ))
    return keyboard