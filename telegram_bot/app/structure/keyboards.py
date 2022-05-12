import math

from aiogram import types

from app.structure.callbacks import struct_cb, Action, partners_list_cb
from src.middlewares.user_database.check_user import UserData
from src.utils.lang_selector import lang_selector
from src.models import InviteTree

async def struct_menu_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_partners', db_user.lang_id),
        callback_data=struct_cb.new(action=Action.show_partners)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_send_to_partners', db_user.lang_id),
        callback_data=struct_cb.new(action=Action.users_broadcast)
    ))
    return keyboard

async def struct_broadcast_agree_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_send_to_partners_btn_agree', db_user.lang_id),
        callback_data=struct_cb.new(action=Action.users_broadcast_agree)
    ))
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_send_to_partners_btn_revoke', db_user.lang_id),
        callback_data=struct_cb.new(action=Action.users_broadcast_revoke)
    ))
    return keyboard

async def struct_back_keyboard(db_user: UserData, depth: int, page: int):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_send_to_partners_btn_back', db_user.lang_id),
        callback_data=partners_list_cb.new(id=0, depth=depth, page=page, action=Action.back)
    ))
    return keyboard

async def partners_depth_keyboard(db_user: UserData):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=8)
    keyboard.add(*[
        types.InlineKeyboardButton(
            f'{depth}', callback_data=partners_list_cb.new(
                id=0, depth=depth, page=0, action=Action.show_partners_depth
            )
        )
        for depth in set(
            await InviteTree.filter(ancestor_id=db_user.db_id).order_by('depth').values_list('depth', flat=True)
        )
    ])
    return keyboard

async def partners_list_keyboard(db_user: UserData, depth: int, page: int = 0):
    on_page = 4
    partners = await InviteTree.filter(
        ancestor_id=db_user.db_id, depth=depth
    ).prefetch_related('child').offset(page * on_page).limit(on_page + 1)

    count_all = await InviteTree.filter(ancestor_id=db_user.db_id, depth=1).count()

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for partner in partners[:on_page]:
        name = []
        if partner.child.username is not None:
            name.append(partner.child.username)
        else:
            if partner.child.first_name is not None:
                name.append(partner.child.first_name)
            if partner.child.last_name is not None:
                name.append(partner.child.last_name)
        keyboard.add(types.InlineKeyboardButton(
            ' '.join(name),
            callback_data=partners_list_cb.new(id=partner.child.id, page=page, action=Action.choose, depth=depth)
        ))
    btns = []
    if page > 0:
        btns.append(types.InlineKeyboardButton(
            '<',
            callback_data=partners_list_cb.new(id=0, action=Action.edit_page, page=page - 1, depth=depth)
        ))
    btns.append(types.InlineKeyboardButton(
        f'{page + 1}/{math.ceil(count_all / on_page)}',
        callback_data=partners_list_cb.new(id=0, action=Action.nothing, page=page, depth=depth)
    ))
    if len(partners) > on_page:
        btns.append(types.InlineKeyboardButton(
            '>',
            callback_data=partners_list_cb.new(id=0, action=Action.edit_page, page=page + 1, depth=depth)
        ))
    keyboard.add(*btns)
    keyboard.add(types.InlineKeyboardButton(
        await lang_selector.say('struct_show_partners_download_xlsx', db_user.lang_id),
        callback_data=partners_list_cb.new(id=0, page=page, action=Action.download_stats, depth=depth)
    ))
    return keyboard