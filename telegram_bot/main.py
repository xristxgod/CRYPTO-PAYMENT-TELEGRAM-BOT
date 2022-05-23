from time import sleep
from bot_app import *
from config import DB_URL, logger
from aiogram import executor, types
from asyncio import create_task
from tortoise import Tortoise
from src.middlewares.user_database.check_user import UserDatabaseMiddleware
from src.schedules import scheduler
from src.scripts.create_superuser import create_super_user
from src.scripts.init_phrases import init_phrases
from worker_transactions.worker import receiving_transactions


async def on_startup(_):
    await bot.set_my_commands([
        types.BotCommand('start', 'Открыть главное меню')
    ])
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['src.models']}
    )
    await Tortoise.generate_schemas()
    await init_phrases()
    await create_super_user()
    create_task(scheduler())
    create_task(receiving_transactions())


async def on_shutdown(_):
    await Tortoise.close_connections()


if __name__ == '__main__':
    while True:
        try:
            # sleep(1000)
            dp.middleware.setup(UserDatabaseMiddleware())
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown, relax=False)
        except Exception as e:
            logger.error(f'POLLING ERROR: {e}')
