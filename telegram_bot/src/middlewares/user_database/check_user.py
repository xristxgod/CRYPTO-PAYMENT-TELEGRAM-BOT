from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from src.models import TGUser
from aiogram import types


def exists(ret=None):
    def _exists(fn):
        def wrapper(self):
            return fn(self) if not self.is_free() else ret
        return wrapper
    return _exists


class UserData:
    def __init__(self, data: TGUser):
        self.data: TGUser = data

    def __repr__(self):
        return str(self.data)

    async def update(self, **kwargs):
        await TGUser.filter(id=self.id).update(**kwargs)
        self.data = await TGUser.get(id=self.id)

    @property
    def id(self):
        return self.data.tg_id

    @property
    def balance(self):
        return self.data.balance

    @property
    def frozen_balance(self):
        return self.data.frozen_balance

    @property
    def db_id(self):
        return self.data.id

    @property
    def lang_id(self):
        return self.data.lang_id

    @property
    def username(self):
        return self.data.username

    @property
    def full_name(self):
        answer = (f'{self.first_name if self.first_name is not None else ""} '
                  f'{self.last_name if self.last_name is not None else ""}')
        return answer

    @property
    def first_name(self):
        return self.data.first_name

    @property
    def last_name(self):
        return self.data.last_name

    def exists(self) -> bool:
        return self.data is not None


class UserDatabaseMiddleware(LifetimeControllerMiddleware):
    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        if type(obj) is types.message.Message:
            user = UserData(data=await TGUser.get_or_none(tg_id=int(obj.chat.id)))
            data['db_user'] = user
        elif type(obj) is types.callback_query.CallbackQuery:
            user = UserData(data=await TGUser.get_or_none(tg_id=int(obj.message.chat.id)))
            data['db_user'] = user
        else:
            data['db_user'] = UserData(data=None)

    async def post_process(self, obj, data, *args):
        if "db_user" in data:
            del data["db_user"]
