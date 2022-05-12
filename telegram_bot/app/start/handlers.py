from tortoise.transactions import atomic

from app.start.services import create_wallet
from app.start.states import *
from app.start.keyboards import *
from app.base.keyboards import main_keyboard
from app.bot_init import *
from src.models import TGUser, InviteTree

@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE, state='*')
async def start(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    if not db_user.exists():
        params = message.get_full_command()
        if len(params) < 2 or not params[1].isdigit() or not await TGUser.exists(id=int(params[1])):
            return await send_message(message.chat.id, 'not_found_inviter_id', 1)
        await StateRegistrationForm.lang_id.set()
        await update_data(state, inviter_id=params[1])
        await send_message(message.chat.id, 'choose_lang', 1, await lang_choose_keyboard())
    else:
        await start_chat(None, db_user)

@atomic()
@dp.callback_query_handler(choose_lang_cb.filter(), state=StateRegistrationForm.lang_id)
async def get_user_lang(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    lang_id = int(callback_data['id'])
    inviter_id = int(await get_data(state, 'inviter_id'))
    user = await TGUser.create(
        tg_id=query.message.chat.id,
        username=query.message.chat.username,
        first_name=query.message.chat.first_name,
        last_name=query.message.chat.last_name,
        lang_id=lang_id,
        inviter_id=inviter_id
    )
    for node in await InviteTree.filter(child_id=user.inviter_id):
        await InviteTree.create(
            ancestor_id=node.ancestor_id,
            child_id=user.id,
            depth=node.depth + 1
        )
    await InviteTree.create(ancestor_id=user.inviter_id, child_id=user.id, depth=1)
    await create_wallet(user.id)
    await state.finish()
    await start_chat(None, UserData(data=user))

async def start_from_decorator(message: types.Message, state: FSMContext, db_user: UserData):
    if not db_user.exists():
        return await send_message(message.chat.id, 'not_found_inviter_id', 1)
    else:
        await start_chat(None, db_user)

async def start_chat(message: types.Message, db_user: UserData):
    await send_message(db_user.id, 'welcome', db_user.lang_id, await main_keyboard(db_user))