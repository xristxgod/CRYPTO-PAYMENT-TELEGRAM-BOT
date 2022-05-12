from worker.celery_app import celery_app
from src.models import Phrase, Transaction, TransactionStatus

async def on_sending_tx(user, tx):
    await Transaction.filter(tx_hash=tx['transactionHash']).update(status=TransactionStatus.success)

    if user.id != 1:
        text = (
            await Phrase.get(lang_id=user.lang_id, code='transaction_success')
        ).text.format(balance=user.balance)
        celery_app.send_task('worker.celery_worker.send_tg_message', args=[user.tg_id, text])