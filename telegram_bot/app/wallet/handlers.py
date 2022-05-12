from uuid import uuid4
from datetime import datetime, timedelta

import pytz
from tortoise.expressions import F
from tortoise.transactions import atomic

from app.wallet.keyboards import *
from app.wallet.states import PayState
from app.start.services import create_wallet
from app.admin.xlsx_service import get_tx_type
from app.bot_init import *
from worker.celery_app import celery_app
from src.models import Table, Wallet, Transaction, TransactionStatus, TransactionType, TGUser, Purchase, Queue
from config import decimals

@dp.message_handler(lambda message: message.text in lang_selector.get_hotkey('btn_main_wallet'))
async def open_wallet(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    text = await lang_selector.format(
        'main_wallet_text', db_user.lang_id,
        balance="%.4f" % decimals.create_decimal(db_user.balance),
        frozen_balance="%.4f" % decimals.create_decimal(db_user.frozen_balance),
        program_profit=sum(await Transaction.filter(
            type=TransactionType.to_user_from_queue, user_id=db_user.db_id
        ).values_list('value', flat=True)),
        ref_bonus=sum(await Transaction.filter(
            Q(user_id=db_user.db_id), Q(type=TransactionType.referral) | Q(type=TransactionType.to_frozen)
        ).values_list('value', flat=True))
    )
    for table in await Table.filter(is_active=True).order_by('id'):
        purchase = await Purchase.get_or_none(user_id=db_user.db_id, table_id=table.id)
        if await Queue.exists(user_id=db_user.db_id, table_id=table.id):
            status = '✅'
        elif purchase is not None:
            status = '❗'
        elif table.is_active:
            status = '🟠'
        else:
            status = '⏰'
        text += f'{status} {table.name}\n'
    await send_msg_text(message.chat.id, text, await wallet_menu_keyboard(db_user))

@dp.callback_query_handler(wallet_cb.filter(action=Action.add_money))
async def start_add_money(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    wallet = await Wallet.get_or_none(user_id=db_user.db_id)
    if wallet is None:
        wallet = await create_wallet(db_user.db_id)
    text = await lang_selector.format('main_wallet_add_money_text', db_user.lang_id, address=wallet.address)
    await send_msg_text(db_user.id, text)

@atomic()
@dp.callback_query_handler(wallet_cb.filter(action=Action.unfreeze))
async def unfreeze(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    if not await is_unfreeze(db_user.db_id):
        return

    wallet = await Wallet.get(user_id=db_user.db_id)
    await Transaction.create(
        user_id=db_user.db_id,
        value=decimals.create_decimal(db_user.frozen_balance),
        status=TransactionStatus.created,
        tx_hash=str(uuid4()),
        fee=0,
        type=TransactionType.from_frozen,
        sender=None,
        recipient=wallet.address
    )
    await TGUser.filter(id=db_user.db_id).update(balance=F('balance') + F('frozen_balance'))
    await TGUser.filter(id=db_user.db_id).update(frozen_balance=0)
    await open_wallet(query.message, state, UserData(TGUser.get(id=db_user.db_id)))
    await query.message.delete()

@dp.callback_query_handler(wallet_cb.filter(action=Action.withdraw))
async def balance_withdraw(query: types.CallbackQuery, db_user: UserData):
    text = await lang_selector.format(
        'wallet_withdraw_enter_value', db_user.lang_id,
        balance="%.4f" % decimals.create_decimal(db_user.balance)
    )
    await send_msg_text(db_user.id, text)
    await PayState.value.set()

@dp.message_handler(
    lambda message: message.text.replace('.', '', 1).isdigit(),
    content_types=types.ContentTypes.TEXT, state=PayState.value
)
async def balance_withdraw_get_value(message: types.Message, state: FSMContext, db_user: UserData):
    value = decimals.create_decimal(message.text)

    if value < decimals.create_decimal('0.01'):
        await state.finish()
        return await send_message(
            db_user.id, 'wallet_withdraw_value_less_then_0', db_user.lang_id,
            await wallet_menu_keyboard(db_user)
        )

    if value > db_user.balance:
        await state.finish()
        return await send_message(
            db_user.id, 'wallet_withdraw_value_enter_error_not_enough', db_user.lang_id,
            await wallet_menu_keyboard(db_user)
        )
    await update_data(state, value=message.text)
    await send_message(db_user.id, 'wallet_withdraw_enter_address', db_user.lang_id)
    await PayState.address.set()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=PayState.address)
async def balance_withdraw_get_address(message: types.Message, state: FSMContext, db_user: UserData):
    await update_data(state, address=message.text)
    amount, to_address = await get_data(state, 'value', 'address')
    await PayState.agree.set()
    text = await lang_selector.format(
        'wallet_withdraw_accept_text', db_user.lang_id,
        amount=amount, address=to_address
    )
    await send_msg_text(db_user.id, text, await withdraw_agree_keyboard(db_user))

@dp.callback_query_handler(wallet_cb.filter(action=Action.withdraw_revoke), state=PayState.agree)
async def get_withdraw_revoke(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await query.message.edit_reply_markup(None)
    await state.finish()
    await send_message(db_user.id, 'wallet_withdraw_revoke', db_user.lang_id, await wallet_menu_keyboard(db_user))

@atomic()
@dp.callback_query_handler(wallet_cb.filter(action=Action.withdraw_agree), state=PayState.agree)
async def get_agree_withdraw(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await query.message.edit_reply_markup(None)
    amount, to_address = await get_data(state, 'value', 'address')
    await state.finish()
    wallet = await Wallet.get(user_id=db_user.db_id)
    tx = await Transaction.create(
        user_id=db_user.db_id,
        value=decimals.create_decimal(amount),
        status=TransactionStatus.created,
        tx_hash=None,
        fee=0,
        type=TransactionType.tx_out,
        sender=wallet.address,
        recipient=to_address
    )
    await TGUser.filter(id=db_user.db_id).update(balance=F('balance') - tx.value)
    # ToDo ETA=24h
    celery_app.send_task(
        'worker.celery_worker.withdraw',
        args=[db_user.db_id, tx.id, to_address, amount],
        eta=pytz.UTC.localize(datetime.now() + timedelta(minutes=30)) - timedelta(hours=1)
    )
    await send_message(db_user.id, 'wallet_withdraw_sent', db_user.lang_id)

@dp.message_handler(content_types=types.ContentTypes.ANY, state=PayState.states)
async def balance_withdraw_miss(message: types.Message, state: FSMContext, db_user: UserData):
    await state.finish()
    await send_message(db_user.id, 'wallet_withdraw_enter_miss', db_user.lang_id)

@dp.callback_query_handler(wallet_cb.filter(action=Action.my_buy))
async def show_purchases_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'wallet_data_list', db_user.lang_id, await something_list_keyboard(db_user, False, 0)
    )

@dp.callback_query_handler(purchases_list_cb.filter(action=Action.back))
async def show_purchases_list_back(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'wallet_data_list', db_user.lang_id,
        await something_list_keyboard(db_user, False, int(callback_data['page']))
    )
    await query.message.delete()

@dp.callback_query_handler(purchases_list_cb.filter(action=Action.edit_page))
async def edit_purchases_page_list(
    query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData
):
    try:
        await query.message.edit_reply_markup(await something_list_keyboard(db_user, False, int(callback_data['page'])))
    except:
        pass

@dp.callback_query_handler(purchases_list_cb.filter(action=Action.choose))
async def show_purchases_detail(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    purchase = await Purchase.get(id=int(callback_data['id'])).prefetch_related('table')
    text = await lang_selector.format(
        'wallet_show_purchases_detail', db_user.lang_id,
        name=purchase.table.name,
        cost=purchase.table.cost,
        time=purchase.created_at.strftime('%Y-%m-%d %H:%M:%S')
    )
    await send_msg_text(
        db_user.id, text,
        await just_back_keyboard(db_user, purchases_list_cb, page=int(callback_data['page']))
    )

@dp.callback_query_handler(wallet_cb.filter(action=Action.my_profit))
async def show_profit_list(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'wallet_data_list', db_user.lang_id, await something_list_keyboard(db_user, True, 0)
    )

@dp.callback_query_handler(profit_list_cb.filter(action=Action.back))
async def show_profit_list_back(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await send_message(
        db_user.id, 'wallet_data_list', db_user.lang_id,
        await something_list_keyboard(db_user, True, int(callback_data['page']))
    )
    await query.message.delete()

@dp.callback_query_handler(profit_list_cb.filter(action=Action.edit_page))
async def edit_profit_page_list(
    query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData
):
    try:
        await query.message.edit_reply_markup(await something_list_keyboard(db_user, True, int(callback_data['page'])))
    except:
        pass

@dp.callback_query_handler(profit_list_cb.filter(action=Action.choose))
async def show_profit_detail(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    tx = await Transaction.get(id=callback_data['id'])
    text = await lang_selector.format(
        'wallet_show_profit_detail', db_user.lang_id,
        value="%.4f" % tx.value,
        type=await get_tx_type(tx.type.value),
        time=tx.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    )
    await send_msg_text(
        db_user.id, text,
        await just_back_keyboard(db_user, profit_list_cb, page=int(callback_data['page']))
    )