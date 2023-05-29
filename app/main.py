import time
import logging
from io import BytesIO
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentTypes, InputFile
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

ENTRYTEXT = """
Привет, {}, я бот, который умеет хранить твои файлы.
Для того, чтобы ты мог мною пользоваться, тебе необходимо пройти авторизацию.
Напиши /login, если у тебя уже есть аккаунт.
Напиши /register, если у тебя еще нет аккаунта.
"""

HELPTEXT = """
Доступные команды:
/login - авторизация в боте
/register - регистрация в боте
"""

class Form(StatesGroup):
    choice = State()  # Will be represented in storage as 'Form:name'

class Auth(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """
    Стартовый хендлер для всех пользователей
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'%{time.asctime()} %{user_id=}'
                 f' {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           ENTRYTEXT.format(message.from_user.username))  # прислать сообщение


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    """
    Функция, обрабатывающая запрос на вывод справки по боту
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} '
                 f'{user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           HELPTEXT.format(message.from_user.username))  # прислать сообщение

@dp.message_handler(commands=['login'])
async def login_handler(message: types.Message):
    """
    Функция, обрабатывающая авторизацию пользователей
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    login_message = """
    Привет, {}, ты попал в эндпоинт /login.
    """
    logging.info(f'{time.asctime()} {user_id=}'
                 f' {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           login_message.format(message.from_user.username))  # прислать сообщение


@dp.message_handler(commands=['register'])
async def register_handler(message: types.Message):
    """
    Функция, обрабатывающая регистрацию пользователей
    :param message:
    :return:
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    register_message = """
    Привет, {}, ты попал в эндпоинт /register.
    """
    logging.info(f'{time.asctime()} {user_id=}'
                 f' {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    await bot.send_message(user_id,
                           register_message.format(message.from_user.username))  # прислать сообщение


@dp.message_handler(content_types=ContentTypes.DOCUMENT)
async def document_sent_by_user(message: types.Message):
    """
    Функция, которая принимает пользовательские файлы
    :param message:
    :return nothing:
    """
    logging.info('uploading file to server')
    file_name = message.document.file_name
    #my_file = open(file_name, "w+")
    print(message.document)
    result = await bot.download_file_by_id(message.document.file_id)
    #print(result)
    #print(bytes(result.read()))
    #fail = InputFile(filename="aboba", path_or_bytesio=result)
    #print(fail)
    fail = InputFile(filename=file_name, path_or_bytesio=BytesIO(bytes(result.read())))
    #result = bytes(result.read())
    #print(result)
    #await bot.download_file('.')
    #typing.BinaryIO
    #my_file.write(message.document)
    #my_file.close()
    await bot.send_message(message.from_user.id, file_name)
    #await bot.send_file(message.document.mime_type,file=result)
    #await bot.send_document(message.from_user.id, document=InputFile(filename=message.document.file_name, path_or_bytesio=await bot.download_file_by_id(message.document.file_id)))
    await bot.send_document(message.from_user.id, document=fail)


if __name__ == '__main__':
    print('bebra')
    executor.start_polling(dp)