from uuid import uuid4

from tortoise.expressions import F
from tortoise.transactions import atomic

from worker.celery_app import celery_app
from worker.services.buy_new_programme import create_transaction_pair
from src.models import Queue, TGUser, Table, TransactionType, Transaction, TransactionStatus, Wallet, Phrase
from config import logger

@atomic()
async def add_to_queue_service(user_id: int, table_id: int):
    try:
        table = await Table.get(id=table_id)

        if await Queue.exists(table_id=table_id, user_id=user_id, got_money=False):
            wallet = await Wallet.get(user_id=user_id)
            user = await TGUser.get(id=user_id)
            await Transaction.create(
                user_id=user_id,
                value=table.cost,
                status=TransactionStatus.success,
                tx_hash=str(uuid4()),
                fee=0,
                type=TransactionType.revoke,
                sender=None,
                recipient=wallet.address,
                table_id=table_id
            )
            await TGUser.filter(id=user_id).update(frozen_balance=F('frozen_balance') + table.cost)
            text = (await Phrase.get(lang_id=user.lang_id, code='revoke_queue_tx')).text
            celery_app.send_task('worker.celery_worker.send_tg_message', args=[user.tg_id, text])
            return

        await Queue.create(table_id=table_id, user_id=user_id, got_money=False, with_balance=True)
        while True:
            nodes_ids = await Queue.filter(table_id=table_id, with_balance=True).order_by('added_at').limit(2).values_list('id', flat=True)
            if len(nodes_ids) < 2:
                break
            first = await Queue.filter(got_money=False, table_id=table_id).order_by('added_at').first()
            user = await TGUser.get(id=first.user_id)
            await Queue.filter(id=first.id).update(got_money=True, with_balance=False)
            await Queue.filter(id__in=nodes_ids).update(with_balance=False)
            await Queue.create(table_id=table_id, user_id=user.id, got_money=False, with_balance=True)
            await create_transaction_pair(
                user, table.cost, TransactionType.to_user_from_queue, 'queue_notify', table_id=table_id
            )
    except Exception as e:
        logger.error(f'ADD TO QUEUE ERROR: {e}')