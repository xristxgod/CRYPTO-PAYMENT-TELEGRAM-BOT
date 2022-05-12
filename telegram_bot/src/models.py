from enum import IntEnum
from tortoise import fields, models

class Lang(models.Model):
    id = fields.IntField(pk=True)
    lang = fields.ForeignKeyField('models.Lang', related_name='phrases', on_delete=fields.CASCADE)
    code = fields.CharField(max_length=250)
    text = fields.TextField()

class Phrase(models.Model):
    id = fields.IntField(pk=True)
    lang = fields.ForeignKeyField('models.Lang', related_name='phrases', on_delete=fields.CASCADE)
    code = fields.CharField(max_length=250)
    text = fields.TextField()

class TGUser(models.Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=255, null=True, default=None)
    first_name = fields.CharField(max_length=255, null=True, default=None)
    last_name = fields.CharField(max_length=255, null=True, default=None)
    balance = fields.DecimalField(max_digits=28, decimal_places=18, default=0.0)
    frozen_balance = fields.DecimalField(max_digits=28, decimal_places=18, default=0.0)
    created_at = fields.DatetimeField(auto_now_add=True)
    inviter = fields.ForeignKeyField(
        'models.TGUser', related_name='childs', on_delete=fields.SET_NULL,
        null=True, default=None
    )
    lang = fields.ForeignKeyField('models.Lang', related_name='users', on_delete=fields.SET_NULL, default=1, null=True)
    wallet: fields.ReverseRelation['Wallet']

    class Meta:
        allow_cycles = True

class Wallet(models.Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(max_length=43)
    private_key = fields.CharField(max_length=255)
    public_key = fields.CharField(max_length=255)
    user = fields.OneToOneField('models.TGUser', related_name='wallet', on_delete=fields.CASCADE)

class InviteTree(models.Model):
    id = fields.BigIntField(pk=True)
    ancestor = fields.ForeignKeyField(
        'models.TGUser', related_name='ancestors', on_delete=fields.SET_NULL, default=None, null=True
    )
    child = fields.ForeignKeyField(
        'models.TGUser', related_name='children', on_delete=fields.SET_NULL, default=None, null=True
    )
    depth = fields.IntField()

class Table(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20)
    cost = fields.DecimalField(max_digits=28, decimal_places=18)
    is_active = fields.BooleanField(default=False)
    before_id = fields.IntField(null=True)

    class Meta:
        ordering = ('id',)

class Queue(models.Model):
    id = fields.BigIntField(pk=True)
    table = fields.ForeignKeyField('models.Table', related_name='tables_invite_tree', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.TGUser', related_name='queues', on_delete=fields.CASCADE)
    added_at = fields.DatetimeField(auto_now_add=True)
    got_money = fields.BooleanField(default=False)
    with_balance = fields.BooleanField(default=True)


class TransactionStatus(IntEnum):
    created = 0
    pending = 1
    success = 2
    error = 3


class TransactionType(IntEnum):
    to_user_for_buy_table = 1
    to_user_from_queue = 2
    referral = 3
    tx_in = 4
    tx_out = 5
    to_frozen = 6
    from_frozen = 7
    buy_table = 8
    buy_queue = 9
    revoke = 10


class FreezeReferralPayment(models.Model):
    id = fields.UUIDField(pk=True)
    value = fields.DecimalField(max_digits=28, decimal_places=18)
    created_at = fields.DatetimeField(auto_now_add=True)
    from_user = fields.ForeignKeyField('models.TGUser', related_name='lost_ref_payment_from', on_delete=fields.CASCADE)
    to_user = fields.ForeignKeyField('models.TGUser', related_name='lost_ref_payment_to', on_delete=fields.CASCADE)
    table = fields.ForeignKeyField('models.Table', related_name='lost_ref_payment', on_delete=fields.CASCADE)
    is_unfrozen = fields.BooleanField(default=False)
    is_second_child = fields.BooleanField(default=False)


class Transaction(models.Model):
    id = fields.UUIDField(pk=True)
    tx_hash = fields.CharField(max_length=255, default=None, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    value = fields.DecimalField(max_digits=28, decimal_places=18)
    fee = fields.DecimalField(max_digits=28, decimal_places=18)
    status = fields.IntEnumField(TransactionStatus)
    type = fields.IntEnumField(TransactionType)
    sender = fields.CharField(max_length=43, default=None, null=True)
    recipient = fields.CharField(max_length=43, default=None, null=True)
    user = fields.ForeignKeyField(
        'models.TGUser', related_name='transactions', on_delete=fields.SET_NULL,
        null=True, default=None
    )
    table = fields.ForeignKeyField(
        'models.Table', related_name='transactions', on_delete=fields.SET_NULL, default=None, null=True
    )


class Purchase(models.Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.TGUser', related_name='purchases', on_delete=fields.CASCADE)
    table = fields.ForeignKeyField('models.Table', related_name='purchases', on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    transaction = fields.ForeignKeyField(
        'models.Transaction', related_name='purchases', on_delete=fields.CASCADE, null=True
    )
    is_after_worker = fields.BooleanField(default=False)

    class Meta:
        unique_together = ('user_id', 'table_id')