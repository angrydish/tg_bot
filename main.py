# Импортируем необходимые модули
from aiogram import executor

from handlers.misc_handlers import misc_handlers
from handlers.login_handlers import authorization
from handlers.register_handlers import registration
from handlers.file_handlers import register_file_handlers

from app.bot import dp

def register_all_handlers(dp):
    misc_handlers(dp)
    register_file_handlers(dp)
    authorization(dp)
    registration(dp)


# Запускаем бота
if __name__ == "__main__":
    print('starting...')
    register_all_handlers(dp)
    executor.start_polling(dp)
