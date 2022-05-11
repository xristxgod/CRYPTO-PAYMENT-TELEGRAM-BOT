from tortoise import fields, models

class UserModel(models.Model):
    id = fields.BigIntField(pk=True, null=False, unique=True)
    username = fields.CharField(max_length=255, null=True, default=None)
    balance = fields.DecimalField(max_digits=28, decimal_places=18, default=0.0)

    class Meta:
        allow_cycles = True