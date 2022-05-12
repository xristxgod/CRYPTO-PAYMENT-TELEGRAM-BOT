from tortoise.expressions import F

from worker.celery_app import celery_app
from src.models import Phrase, TransactionStatus, Transaction, TransactionType, TGUser
from config import decimals

async def on_receiving(user, tx):
    text = (await Phrase.get(lang_id=user.lang_id, code='transaction_success')).text.format(
        balance="%.4f" % (decimals.create_decimal(user.balance) + decimals.create_decimal(tx['amount']))
    )
    celery_app.send_task('worker.celery_worker.send_tg_message', args=[user.tg_id, text])
    await TGUser.filter(id=user.id).update(balance=F('balance') + decimals.create_decimal(tx['amount']))

    await Transaction.create(
        tx_hash=tx['transactionHash'],
        value=tx['amount'],
        fee=tx['fee'],
        type=TransactionType.tx_in,
        status=TransactionStatus.success,
        sender=tx['sender'],
        recipient=tx['recipient'],
        user_id=user.id
    )