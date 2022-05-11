from aiogram import executor, types
from tortoise import Tortoise

from bot_app.__init__ import dp, bot
from src.middlewares.__init__ import UserDatabaseMiddleware
from config import Config, logger

async def on_startup(_):
    await bot.set_my_commands([
        types.BotCommand('start', "Open main menu")
    ])
    await Tortoise.init(
        db_url=Config.DATABASE_URL,
        modules={"models": ["src.models"]}
    )
    await Tortoise.generate_schemas()

async def on_shutdown(_):
    await Tortoise.close_connections()

if __name__ == '__main__':
    # Run bot
    try:
        dp.middleware.setup(UserDatabaseMiddleware())
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown, relax=False)
    except Exception as error:
        logger.error(f"ERROR: {error}")