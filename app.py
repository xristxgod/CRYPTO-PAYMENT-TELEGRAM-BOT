from aiogram import executor

from bot_app.__init__ import db

if __name__ == '__main__':
    # Run bot
    executor.start_polling(db, skip_updates=True)