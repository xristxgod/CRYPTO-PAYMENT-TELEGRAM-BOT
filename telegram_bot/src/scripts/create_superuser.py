from bot_app.start.services import create_wallet
from config import logger, decimals
from src.models import TGUser, Table, Queue, Purchase


async def create_super_user():
    """Script for creating first user in system"""
    existing_user = await TGUser.get_or_none(id=1)
    if existing_user is not None:
        logger.error('Super admin already exists')
        return

    user = await TGUser.create(
        id=1,
        tg_id=1,
        username='admin',
        first_name='admin',
        last_name='admin',
        lang_id=1,
    )
    await create_wallet(user.id)
    last_id = None
    for table_name, cost in [
        ('0.1 BNB', decimals.create_decimal('0.1')),
        ('0.2 BNB', decimals.create_decimal('0.2')),
        ('0.3 BNB', decimals.create_decimal('0.3')),
        ('0.4 BNB', decimals.create_decimal('0.4')),
        ('0.6 BNB', decimals.create_decimal('0.6')),
        ('0.8 BNB', decimals.create_decimal('0.8')),
        ('1 BNB', decimals.create_decimal('1.0')),
        ('1.2 BNB', decimals.create_decimal('1.2')),
        ('1.5 BNB', decimals.create_decimal('1.5')),
        ('2 BNB', decimals.create_decimal('2.0')),
        ('2.5 BNB', decimals.create_decimal('2.5')),
        ('3 BNB', decimals.create_decimal('3.0')),
        ('4 BNB', decimals.create_decimal('4.0')),
        ('5 BNB', decimals.create_decimal('5.0')),
        ('6 BNB', decimals.create_decimal('6.0')),
        ('8 BNB', decimals.create_decimal('8.0')),
    ]:
        last_id = (await Table.create(name=table_name, cost=cost, is_active=False, before_id=last_id)).id
        await Purchase.create(user_id=1, table_id=last_id, transaction_id=None, is_after_worker=True)
        await Queue.create(table_id=last_id, user_id=1, got_money=False, with_balance=False)
    logger.error('Super admin created successfully')