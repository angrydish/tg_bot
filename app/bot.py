import os

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')

# Создаем бота и диспетчера с токеном и хранилищем состояний
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
