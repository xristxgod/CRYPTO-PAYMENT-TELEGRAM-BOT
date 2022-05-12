from typing import Optional

from app.bot_init import *
from app.base.callbacks import close_cb, BaseAction
from app.base.keyboards import main_keyboard

@dp.message_handler(commands=['close'], chat_type=types.ChatType.PRIVATE, state='*')
async def close_any(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    return await send_msg_text(message.chat.id, 'Ok', keyboard=await main_keyboard(db_user))

@dp.callback_query_handler(close_cb.filter(action=BaseAction.close), state='*')
async def close(
        query: types.CallbackQuery,
        db_user: UserData,
        state: Optional[FSMContext] = None
):
    if state is not None:
        await state.finish()
    await send_msg_text(db_user.id, 'ok', await main_keyboard(db_user))
    await query.message.delete()