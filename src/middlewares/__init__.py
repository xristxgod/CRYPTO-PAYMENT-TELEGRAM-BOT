from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from src.models import UserModel
from aiogram import types

def exists(ret=None):
    def _exists(fn):
        def wrapper(self):
            return fn(self) if not self.is_free() else ret
        return wrapper
    return _exists


class UserData:
    def __init__(self, data: UserModel):
        self.data: UserModel = data

    def __repr__(self):
        return str(self.data)

    async def update(self, **kwargs):
        await UserModel.filter(id=self.id).update(**kwargs)
        self.data = await UserModel.get(id=self.id)

    @property
    def id(self):
        return self.data.id

    @property
    def balance(self):
        return self.data.balance

    @property
    def username(self):
        return self.data.username

    def exists(self) -> bool:
        return self.data is not None

class UserDatabaseMiddleware(LifetimeControllerMiddleware):
    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        if type(obj) is types.message.Message:
            user = UserData(data=await UserModel.get_or_none(id=obj.chat.id))
            data["db_user"] = user
        elif type(obj) is types.callback_query.CallbackQuery:
            user = UserData(data=await UserModel.get_or_none(id=int(obj.message.chat.id)))
            data['db_user'] = user
        else:
            data['db_user'] = UserData(data=None)

    async def post_process(self, obj, data, *args):
        if "db_user" in data:
            del data["db_user"]