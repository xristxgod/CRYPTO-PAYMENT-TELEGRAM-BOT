from asyncio import create_task

from app.admin.xlsx_service import get_users_xlsx, get_tx_xlsx, get_tables_xlsx
from app.admin.states import AdminUtilsState
from app.base.callbacks import admin_cb, Action
from app.bot_init import *
from src.models import TGUser
from config import Config

@dp.callback_query_handler(admin_cb.filter(action=Action.excel_users))
async def start_admin_stats(message: types.Message, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    text = f'Пользователей: {len(await TGUser.all())}\n'
    await send_msg_text(db_user.id, text)
    await bot.send_chat_action(db_user.id, types.ChatActions.UPLOAD_DOCUMENT)
    file, name = await get_users_xlsx()
    await bot.send_document(db_user.id, types.InputFile(file, filename=name))

@dp.callback_query_handler(admin_cb.filter(action=Action.excel_transactions))
async def start_admin_stats_transactions(message: types.Message, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    text = f'Статистика транзакций\n'
    await send_msg_text(db_user.id, text)
    await bot.send_chat_action(db_user.id, types.ChatActions.UPLOAD_DOCUMENT)
    file, name = await get_tx_xlsx()
    await bot.send_document(db_user.id, types.InputFile(file, filename=name))

@dp.callback_query_handler(admin_cb.filter(action=Action.excel_programmes))
async def start_admin_stats_tables(message: types.Message, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    text = f'Статистика программ\n'
    await send_msg_text(db_user.id, text)
    await bot.send_chat_action(db_user.id, types.ChatActions.UPLOAD_DOCUMENT)
    file, name = await get_tables_xlsx()
    await bot.send_document(db_user.id, types.InputFile(file, filename=name))

@dp.callback_query_handler(admin_cb.filter(action=Action.broadcast))
async def start_admin_broadcast(message: types.Message, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    await send_msg_text(db_user.id, 'Отправьте сообщение. Оно будет разослано всем пользователям, либо нажмите /close')
    await AdminUtilsState.wait.set()

@dp.message_handler(content_types=types.ContentTypes.ANY, state=AdminUtilsState.wait)
async def start_sending_broadcast(message: types.Message, state: FSMContext, db_user: UserData):
    if db_user.id not in Config.ADMIN_IDS:
        return
    await state.finish()
    await message.answer('Начинаю рассылку')
    create_task(__sending_broadcast(message, db_user))

async def __sending_broadcast(message: types.Message, db_user: UserData):
    for user in await TGUser.all():
        try:
            await bot.copy_message(chat_id=user.tg_id, from_chat_id=db_user.id, message_id=message.message_id)
        except:
            continue