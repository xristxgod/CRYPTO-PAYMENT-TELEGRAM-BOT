from uuid import uuid4
from decimal import Decimal

from tortoise.expressions import F

from worker.celery_app import celery_app
from src.models import (
    TGUser, Table, InviteTree, Purchase, Transaction,
    TransactionStatus, TransactionType, Queue, Phrase, Wallet, FreezeReferralPayment
)
from config import decimals, logger

async def create_transaction_pair(
        user: TGUser, value: Decimal, t: TransactionType, code: str, table_id: int, sender: str = None
):
    amount = value * decimals.create_decimal("0.8")
    frozen = value - amount
    wallet = await Wallet.get(user_id=user.id)
    await Transaction.create(
        user_id=user.id,
        value=amount,
        status=TransactionStatus.success,
        tx_hash=str(uuid4()),
        fee=0,
        type=t,
        sender=sender,
        recipient=wallet.address,
        table_id=table_id
    )
    await Transaction.create(
        user_id=user.id,
        value=frozen,
        status=TransactionStatus.success,
        tx_hash=str(uuid4()),
        fee=0,
        type=TransactionType.to_frozen,
        sender=sender,
        recipient=wallet.address,
        table_id=table_id
    )
    await TGUser.filter(id=user.id).update(balance=F('balance') + amount, frozen_balance=F('frozen_balance') + frozen)
    table = await Table.get(id=table_id)
    text = (await Phrase.get(lang_id=user.lang_id, code=code)).text.format(
        amount="%.4f" % amount,
        frozen="%.4f" % frozen,
        balance="%.4f" % (user.balance + amount),
        frozen_balance="%.4f" % (user.frozen_balance + frozen),
        name=table.name
    )
    celery_app.send_task('worker.celery_worker.send_tg_message', args=[user.tg_id, text])

async def __send_referral(
    paid_user: TGUser, table: Table, is_with_freeze: bool, is_second_child: bool = False, code: str = None
):
    users_ids = await InviteTree.filter(child_id=paid_user.id).values_list('ancestor_id', flat=True)
    users = await TGUser.filter(id__in=users_ids).order_by('-created_at')
    if is_second_child:
        await FreezeReferralPayment.create(
            value=table.cost,
            from_user_id=paid_user.id,
            to_user_id=paid_user.inviter_id,
            table_id=table.id,
            is_second_child=True
        )
        return

    count = 0
    paid_wallet = await Wallet.get(user_id=paid_user.id)
    for index, user in enumerate(users):
        value = decimals.create_decimal((table.cost / 2) if index == 0 else (table.cost / 10))
        if await Purchase.exists(table_id=table.id, is_after_worker=True, user_id=user.id):
            await create_transaction_pair(
                user, value, TransactionType.referral,
                'referral_notify' if code is None else code,
                table_id=table.id, sender=paid_wallet.address
            )
            count += 1
        elif is_with_freeze:
            await FreezeReferralPayment.create(
                value=value,
                from_user_id=paid_user.id,
                to_user_id=user.id,
                table_id=table.id,
                is_second_child=is_second_child
            )
            count += 1
        if count > 5:
            break

    if count != 6:
        wallet = await Wallet.get(user_id=paid_user.id)
        value = table.cost if count == 0 else (table.cost * decimals.create_decimal((6 - count) / 10))
        await Transaction.create(
            user_id=1,
            value=value,
            status=TransactionStatus.success,
            tx_hash=str(uuid4()),
            fee=0,
            type=TransactionType.referral,
            sender=None,
            recipient=wallet.address,
            table_id=table.id
        )
        await TGUser.filter(id=1).update(balance=F('balance') + value)

async def __add_user_to_queue(user_id: int, table_id):
    celery_app.send_task('worker.celery_worker.add_to_queue', args=[user_id, table_id])

async def __unfreeze_referral_payments(user: TGUser, table: Table, is_with_queue: bool):
    freeze_payments = await FreezeReferralPayment.filter(
        to_user_id=user.id, table_id=table.id, is_unfrozen=False
    ).prefetch_related('to_user', 'from_user')
    if len(freeze_payments) == 0:
        return
    for payment in freeze_payments:
        if payment.is_second_child:
            if is_with_queue:
                await __send_referral(payment.from_user, table, True, code='unfrozen_referral_notify')
            else:
                await __add_user_to_queue(user.id, table.id)
        else:
            await create_transaction_pair(
                user=payment.to_user, value=payment.value, t=TransactionType.referral, table_id=table.id,
                code='unfrozen_referral_notify'
            )

    await FreezeReferralPayment.filter(id__in=[x.id for x in freeze_payments]).update(is_unfrozen=True)

async def buy_new_programme_service(user_id: int, table_id: int, is_with_queue: bool, purchase_id: int):
    try:
        user = await TGUser.get(id=user_id)
        table = await Table.get(id=table_id)

        current_line_ids = await InviteTree.filter(
            ancestor_id=user.inviter_id, depth=1).values_list('child_id', flat=True)
        purchases_count = await Purchase.filter(
            table_id=table_id, user_id__in=current_line_ids, is_after_worker=True).count()

        is_inviter_with_purchase = await Purchase.exists(user_id=user.inviter_id, table_id=table_id)
        is_inviter_in_queue = await Queue.exists(user_id=user.inviter_id, table_id=table_id)

        if purchases_count == 0:
            await __send_referral(user, table, True)
        elif purchases_count == 1:
            if is_inviter_in_queue:
                await __send_referral(user, table, False)
            elif is_inviter_with_purchase:
                await __add_user_to_queue(user.inviter_id, table.id)
            else:
                await __send_referral(user, table, True, is_second_child=True)
        else:
            await __send_referral(user, table, False)

        if is_with_queue:
            await __add_user_to_queue(user.id, table.id)

        await Purchase.filter(id=purchase_id).update(is_after_worker=True)

        await __unfreeze_referral_payments(user, table, is_with_queue)
    except Exception as e:
        logger.error(f'ERROR: {e}')