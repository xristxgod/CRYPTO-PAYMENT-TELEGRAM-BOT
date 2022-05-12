from uuid import uuid4

from tortoise.expressions import Q, F
from tortoise.transactions import atomic

from app.programmes.keyboards import *
from app.bot_init import *
from src.models import Table, Wallet, Transaction, TransactionStatus, TransactionType, TGUser, InviteTree, Queue
from worker.celery_app import celery_app
from worker_xlsx.celery_app import celery_xlsx_app
from config import decimals

@dp.message_handler(lambda message: message.text in lang_selector.get_hotkey('btn_main_programmes'))
async def open_programmes(message: types.Message, state: FSMContext, db_user: UserData):
    if state is not None:
        await state.finish()
    await send_message(
        message.chat.id, 'main_programmes_text', db_user.lang_id, await programmes_menu_keyboard(db_user)
    )

@dp.callback_query_handler(programmes_cb.filter(action=Action.back))
async def open_programmes_from_query(
    query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData
):
    await query.message.edit_reply_markup(None)
    await open_programmes(query.message, state, db_user)

@dp.callback_query_handler(programmes_cb.filter(action=Action.revoke))
@dp.callback_query_handler(programmes_cb.filter(action=Action.choose))
async def open_program_detail(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await query.message.edit_reply_markup(None)

    table_id = int(callback_data['id'])
    table = await Table.get(id=table_id)

    purchase = await Purchase.get_or_none(user_id=db_user.db_id, table_id=table_id)

    if await Queue.exists(user_id=db_user.db_id, table_id=table_id):
        status = '✅'
        code = 'programmes_detail_text'
    elif purchase is not None:
        status = '❗'
        code = 'programmes_detail_text_without_queue'
    elif table.is_active:
        status = '🟠'
        code = 'programmes_buy_text'
    else:
        text = await lang_selector.format(
            'programmes_detail_text_is_inactive', db_user.lang_id, status='⏰', name=table.name,
        )
        return await send_msg_text(db_user.id, text)

    count = await Purchase.filter(
        user_id__in=await InviteTree.filter(ancestor_id=db_user.db_id).values_list('child_id', flat=True),
        table_id=table.id
    ).count()

    if purchase is not None:
        profit = sum(await Transaction.filter(
            Q(user_id=db_user.db_id), Q(table_id=table_id),
            Q(type=TransactionType.referral) | Q(type=TransactionType.to_frozen) | Q(type=TransactionType.to_user_from_queue)
        ).values_list('value', flat=True))
        text = await lang_selector.format(
            code, db_user.lang_id,
            name=table.name, time=purchase.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            count=count, profit="%.6f" % profit, status=status
        )
        keyboard = await program_detail_keyboard(table, db_user)
    else:
        text = await lang_selector.format(
            code, db_user.lang_id, name=table.name, balance="%.4f" % db_user.balance, count=count, status=status
        )
        keyboard = await program_buy_detail_keyboard(table, db_user)
    await send_msg_text(db_user.id, text, keyboard)

@dp.callback_query_handler(programmes_cb.filter(action=Action.buy))
async def buying_agree(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await __show_alarm(query, callback_data, db_user, False)

@dp.callback_query_handler(programmes_cb.filter(action=Action.buy_with_qualification))
async def buying_agree_qual(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await __show_alarm(query, callback_data, db_user, True)

@dp.callback_query_handler(programmes_cb.filter(action=Action.buy_qualification_only))
async def buying_agree_qual_only(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await query.message.edit_reply_markup(None)
    table_id = int(callback_data['id'])
    table = await Table.get(id=table_id)
    await send_message(
        db_user.id, 'programmes_btn_buy_agree', db_user.lang_id,
        await program_buy_qual_only_agree_keyboard(table, db_user)
    )

async def __show_alarm(query: types.CallbackQuery, callback_data: dict, db_user: UserData, is_qual: bool):
    await query.message.edit_reply_markup(None)
    table_id = int(callback_data['id'])
    table = await Table.get(id=table_id)
    await send_message(
        db_user.id, 'programmes_btn_buy_agree', db_user.lang_id,
        await program_buy_agree_keyboard(table, db_user, is_qual)
    )

@dp.callback_query_handler(programmes_cb.filter(action=Action.buy_agree))
async def just_buy_agree(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await __buy_table_with_rabbit_mq(query, callback_data, db_user, False)

@dp.callback_query_handler(programmes_cb.filter(action=Action.buy_with_qualification_agree))
async def qual_buy_agree(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    await __buy_table_with_rabbit_mq(query, callback_data, db_user, True)

@atomic()
@dp.callback_query_handler(programmes_cb.filter(action=Action.buy_qualification_only_agree))
async def buy_qualification_only_agree(
    query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData
):
    table_id = int(callback_data['id'])
    if await Queue.exists(user_id=db_user.db_id, table_id=table_id):
        return

    table = await Table.get(id=table_id)
    wallet = await Wallet.get(user_id=db_user.db_id)
    user = await TGUser.get(id=db_user.db_id)

    if user.balance + user.frozen_balance < table.cost:
        return await send_message(
            db_user.id, 'programmes_buy_not_enough_balance', db_user.lang_id, await programmes_menu_keyboard(db_user)
        )

    if user.frozen_balance >= table.cost:
        await TGUser.filter(id=user.id).update(frozen_balance=F('frozen_balance') - table.cost)
    else:
        cost = table.cost - user.frozen_balance
        await TGUser.filter(id=user.id).update(balance=F('balance') - cost, frozen_balance=0)

    await Transaction.create(
        user_id=db_user.db_id,
        value=table.cost,
        status=TransactionStatus.success,
        tx_hash=str(uuid4()),
        fee=0,
        type=TransactionType.buy_queue,
        sender=wallet.address,
        recipient=None,
        table_id=table_id
    )
    celery_app.send_task('worker.celery_worker.add_to_queue', args=[db_user.db_id, table_id])
    await send_message(db_user.id, 'programmes_buy_success', db_user.lang_id, await programmes_menu_keyboard(db_user))

@atomic()
async def __buy_table_with_rabbit_mq(query: types.CallbackQuery, callback_data: dict, db_user: UserData, is_qual: bool):
    await query.message.edit_reply_markup(None)
    table_id = int(callback_data['id'])
    table = await Table.get(id=table_id)
    user = await TGUser.get(id=db_user.db_id)
    if table.before_id is not None and not await Purchase.exists(user_id=user.id, table_id=table.before_id):
        return await send_message(
            db_user.id, 'programmes_buy_error', db_user.lang_id, await programmes_menu_keyboard(db_user)
        )

    cost = table.cost * 2 if is_qual else table.cost

    if user.balance + user.frozen_balance < cost:
        return await send_message(
            db_user.id, 'programmes_buy_not_enough_balance', db_user.lang_id, await programmes_menu_keyboard(db_user)
        )
    wallet = await Wallet.get(user_id=user.id)
    if user.frozen_balance >= cost:
        await TGUser.filter(id=user.id).update(frozen_balance=F('frozen_balance') - cost)
    else:
        cost = cost - user.frozen_balance
        await TGUser.filter(id=user.id).update(balance=F('balance') - cost, frozen_balance=0)
    tx = await Transaction.create(
        user_id=db_user.db_id,
        value=decimals.create_decimal(cost),
        status=TransactionStatus.success,
        tx_hash=str(uuid4()),
        fee=0,
        type=TransactionType.buy_table,
        sender=wallet.address,
        recipient=None,
        table_id=table_id
    )
    purchase = await Purchase.create(user_id=user.id, table_id=table_id, transaction_id=tx.id)

    celery_app.send_task(
        'worker.celery_worker.buy_new_programme',
        args=[user.id, table.id, is_qual, purchase.id],
        countdown=5
    )
    await send_message(db_user.id, 'programmes_buy_success', db_user.lang_id, await programmes_menu_keyboard(db_user))

@dp.callback_query_handler(programmes_cb.filter(action=Action.show_queue))
async def show_queue(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    table = await Table.get(id=int(callback_data['id']))
    current = await Queue.filter(table_id=table.id, user_id=db_user.db_id, got_money=False).first()
    l_q = await Queue.filter(table_id=table.id, got_money=True).order_by('added_at').first()
    if l_q is None:
        count_before_last = 1
    else:
        count_before_last = await Queue.filter(table_id=table.id, added_at__lte=l_q.added_at).count()

    if await Queue.exists(user_id=db_user.db_id, table_id=table.id):
        status = '✅'
    elif await Purchase.exists(user_id=db_user.db_id, table_id=table.id):
        status = '❗'
    else:
        status = '🟠'

    if current is None:
        text = await lang_selector.say('programmes_queue_info_not_exists', db_user.lang_id)
        text = text.format(name=table.name, current_name=count_before_last, status=status)
    else:

        text = await lang_selector.say('programmes_queue_info', db_user.lang_id)
        count_user = await Queue.filter(table_id=table.id, user_id=db_user.db_id, got_money=True).count()
        text = text.format(
            name=table.name, status=status,
            count_user=count_user,
            profit="%.6f" % (count_user * table.cost)
        )
    await send_msg_text(db_user.id, text, await program_buy_agree_keyboard(table, db_user, False, True))

@dp.callback_query_handler(programmes_cb.filter(action=Action.download_stats))
async def download_stats(query: types.CallbackQuery, callback_data: dict, state: FSMContext, db_user: UserData):
    table_id = int(callback_data['id'])
    await send_message(db_user.id, 'programmes_download_file', db_user.lang_id)
    celery_xlsx_app.send_task('worker_xlsx.celery_worker.send_table_xlsx', args=[db_user.db_id, table_id])
    await bot.send_chat_action(db_user.id, types.ChatActions.UPLOAD_DOCUMENT)