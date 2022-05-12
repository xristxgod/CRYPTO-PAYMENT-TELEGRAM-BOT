from app.base.handlers import dp, bot, main_keyboard
from app.start.handlers import dp
from app.admin.handlers import dp
from app.extra.handlers import dp
from app.wallet.handlers import dp
from app.programmes.handlers import dp
from app.structure.handlers import dp
from app.bot_init import types, send_msg_text, UserData
from config import logger

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def get_some_trash(message: types.Message, db_user: UserData):
    logger.error(f'GET SOME MSG: {message}')
    return await send_msg_text(message.chat.id, 'Opening the menu', keyboard=await main_keyboard(db_user))

__all__ = ['dp', 'bot']