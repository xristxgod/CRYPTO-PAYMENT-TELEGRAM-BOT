from tortoise import fields, models

class Lang(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

class Phrase(models.Model):
    id = fields.IntField(pk=True)
    lang = fields.ForeignKeyField('models.Lang', related_name='phrases', on_delete=fields.CASCADE)
    code = fields.CharField(max_length=250)
    text = fields.TextField()

class UserModel(models.Model):
    id = fields.BigIntField(pk=True, null=False, unique=True)
    username = fields.CharField(max_length=255, null=True, default=None)
    balance = fields.DecimalField(max_digits=28, decimal_places=18, default=0.0)

    lang = fields.ForeignKeyField('models.Lang', related_name='users', on_delete=fields.SET_NULL, default=1, null=True)

    class Meta:
        allow_cycles = True