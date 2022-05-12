from asyncio import create_task

from tortoise.expressions import Q

from app.structure.keyboards import *
from app.structure.states import *
from app.bot_init import *
from worker_xlsx.celery_app import celery_xlsx_app
from src.models import Table, Wallet, Transaction, TransactionType, TGUser, Purchase, InviteTree

@dp.message_handler(lambda message: message.text in lang_selector.get_hotkey('btn_main_struct'))
async def open_struct(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()

    counts = ""
    depths = await InviteTree.filter(ancestor_id=db_user.db_id).order_by('depth').values_list('depth', flat=True)
    _line_text = await lang_selector.say('struct_count_lines_row', db_user.lang_id)
    count_all_is_struct = 0
    s_profit = 0
    for depth in set(depths):
        users_ids = await InviteTree.filter(ancestor_id=db_user.db_id, depth=depth).values_list('child_id', flat=True)
        count_all_is_struct += len(users_ids)
        profit = sum(await Transaction.filter(
            Q(user_id=db_user.db_id),
            Q(type=TransactionType.referral) | Q(type=TransactionType.to_frozen) | Q(type=TransactionType.to_user_from_queue),
            Q(sender__in=await Wallet.filter(user_id__in=users_ids).values_list('address', flat=True))
        ).values_list('value', flat=True))
        s_profit += profit
        counts += _line_text.format(depth=depth, count=len(users_ids), referrals="%.6f" % profit) + '\n'
    text = await lang_selector.format(
        'struct_show_partners_main_text', db_user.lang_id,
        count_all=len(set(await Purchase.all().values_list('user_id', flat=True))),
        counts=counts.replace('\n\n', '\n'),
        ref=f'https://t.me/{(await bot.get_me()).username}?start={db_user.db_id}',
        count=count_all_is_struct,
        profit=s_profit
    )
    await send_msg_text(message.chat.id, text, await struct_menu_keyboard(db_user))

@dp.callback_query_handler(struct_cb.filter(action=Action.users_broadcast))
async def start_users_broadcast(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await UserBroadcastState.text.set()
    await send_message(db_user.id, 'struct_show_send_to_partners_text', db_user.lang_id)

@dp.message_handler(content_types=types.ContentTypes.ANY, state=UserBroadcastState.text)
async def get_text(message: types.Message, state: FSMContext, db_user: UserData):
    await update_data(state, text=message.message_id)
    await send_message(
        db_user.id, 'struct_show_send_to_partners_agree', db_user.lang_id,
        await struct_broadcast_agree_keyboard(db_user)
    )
    await UserBroadcastState.agree.set()

async def __start_broadcast(user_id: int, tg_id: int, message_id: int):
    targets_ids = await InviteTree.filter(ancestor_id=user_id, depth=1).values_list('child_id', flat=True)
    users = await TGUser.filter(id__in=targets_ids)
    for user in users:
        try:
            await send_message(user.tg_id, 'is_uplainer_message', user.lang_id)
            await bot.copy_message(user.tg_id, tg_id, message_id)
        except:
            continue

@dp.callback_query_handler(struct_cb.filter(action=Action.users_broadcast_agree), state=UserBroadcastState.agree)
async def get_agree(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    message_id = int(await get_data(state, 'text'))
    create_task(__start_broadcast(db_user.db_id, db_user.id, message_id))
    await send_message(
        db_user.id, 'struct_show_send_to_partners_started', db_user.lang_id,
        await struct_menu_keyboard(db_user)
    )
    await state.finish()
    await query.message.delete()

@dp.callback_query_handler(struct_cb.filter(action=Action.users_broadcast_revoke), state=UserBroadcastState.agree)
async def get_not_agree(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'struct_show_send_to_partners_btn_revoke', db_user.lang_id,
        await struct_menu_keyboard(db_user)
    )
    await state.finish()
    await query.message.delete()

@dp.callback_query_handler(struct_cb.filter(action=Action.show_partners))
async def show_partners_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(db_user.id, 'struct_show_partners_depth', db_user.lang_id, await partners_depth_keyboard(db_user))

@dp.callback_query_handler(partners_list_cb.filter(action=Action.show_partners_depth))
async def show_partners_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'struct_show_partners', db_user.lang_id,
        await partners_list_keyboard(db_user, int(callback_data['depth']), 0)
    )

@dp.callback_query_handler(partners_list_cb.filter(action=Action.back))
async def show_partners_list_back(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'struct_show_partners', db_user.lang_id,
        await partners_list_keyboard(db_user, int(callback_data['depth']), int(callback_data['page']))
    )
    await query.message.delete()

@dp.callback_query_handler(partners_list_cb.filter(action=Action.edit_page))
async def edit_page_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    try:
        await query.message.edit_reply_markup(
            await partners_list_keyboard(db_user, int(callback_data['depth']), int(callback_data['page']))
        )
    except:
        pass

@dp.callback_query_handler(partners_list_cb.filter(action=Action.choose))
async def show_partner_detail(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    partner = await TGUser.get(id=int(callback_data['id']))
    text = await lang_selector.format(
        'struct_show_partners_detail', db_user.lang_id,
        name=partner.username if partner.username is not None else (
            partner.first_name if partner.first_name is not None else partner.last_name
        )
    )
    user_tables_ids = await Purchase.filter(user_id=db_user.db_id).values_list('table_id', flat=True)
    for table in await Table.filter(is_active=True).order_by('id'):
        text += f'{"✅" if table.id in user_tables_ids else "❌"} {table.name}\n'
    await send_msg_text(
        db_user.id, text,
        await struct_back_keyboard(db_user, depth=int(callback_data['depth']), page=int(callback_data['page']))
    )

@dp.callback_query_handler(partners_list_cb.filter(action=Action.download_stats))
async def download_stats(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(db_user.id, 'struct_show_partners_download_xlsx_start', db_user.lang_id)
    celery_xlsx_app.send_task(
        'worker_xlsx.celery_worker.send_partners_xlsx',
        args=[db_user.db_id, int(callback_data['depth'])]
    )
    await bot.send_chat_action(db_user.id, types.ChatActions.UPLOAD_DOCUMENT)