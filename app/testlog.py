# Импортируем необходимые модули
import io
import re
import os
import time
import sched
from datetime import datetime
from io import BytesIO
import threading
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Chat, ContentTypes, InputFile


from dotenv import load_dotenv

from models.models import *
from db.config import host, port, password, database, user
from db.db import *

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')
# Создаем бота и диспетчера с токеном и хранилищем состояний

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = DB({
    'host':host,
    'port':port,
    'database':database,
    'user':user,
    'password':password})
print(db.execute_one('test_query'))
db.execute_none('create_database')


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("/login"))
keyboard.add(KeyboardButton("/register"))
keyboard.add(KeyboardButton("/delete"))

keyboard_cancel=ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_cancel.add("/cancel")


# Определяем класс состояний для авторизации
class Auth(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class Reg(StatesGroup):
    wait_for_username = State()
    wait_for_password = State()
    wait_for_password_2 = State()

class AuthorizedPerson(StatesGroup):
    wait_for_upload_file = State()
    wait_for_download_file = State()

# Создаем хэндлер для команды /start, которая запускает процесс авторизации

bot_messages = []
from_bot_messages = []

def check_and_delete():
    print(bot_messages)
    pass
    # if bot_messages is not None or bot_messages is not []:
    #     latest_message_time = bot_messages[-1]
    #     pass



@dp.message_handler(commands="delete")
async def delete_messages(message: types.Message):

    chat_id = message.chat.id
    # Добавляем идентификатор команды в список
    bot_messages.append(message)
    # Удаляем все сообщения из списка по одному
    for message in bot_messages:
        try:
            await bot.delete_message(chat_id, message.message_id)
        except:
            pass
    for message in from_bot_messages:
        #print(message_id)
        try:
            await message.delete()
        except:
            pass
    # Очищаем список
    bot_messages.clear()


@dp.message_handler(commands="exit")
async def delete_messages(message: types.Message):
    chat_id = message.chat.id
    # Добавляем идентификатор команды в список
    bot_messages.append(message)
    # Удаляем все сообщения из списка по одному
    for message_id in bot_messages:
        await bot.delete_message(chat_id, message_id)
    # Очищаем список
    bot_messages.clear()


@dp.message_handler(commands="start")
async def login(message: types.Message):
    bot_messages.append(message)
    a = message.date
    b=datetime.now()
    print(a, b, sep="\n")
    print(b-a)
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg = await message.answer("Привет! Добро пожаловать в мой бот.", reply_markup=keyboard)
    from_bot_messages.append(msg)
    # Переводим пользователя в состояние ожидания имени пользователя



@dp.message_handler(content_types=['document','audio','video'])
async def document_sent_by_user(message: types.Message):
    """
    Функция, которая принимает пользовательские файлы
    :param message:
    :return nothing:
    """
    file_src = object
    content_type = message.content_type
    # get file object by content type
    if content_type == "document":
        file_src = message.document
    elif content_type == "audio":
        file_src = message.audio
    elif content_type == "video":
        file_src = message.video


    logging.info('uploading file to server')
    file_name = file_src.file_name
    print(file_name)
    print( message.content_type)
    print(file_src)
    #print(message.audio.)
    #result = await bot.download_file_by_id(message.audio.file_id)
    #fail = InputFile(filename=file_name, path_or_bytesio=BytesIO(bytes(result.read()))) # получили файл, можно загрузить в бд

    print('1st stage')
    file = await bot.get_file(file_src.file_id)
    print('2nd stage')
    file = await bot.download_file(file.file_path)
    xd = bytes.fromhex( file.read().hex())

    print('uploading')
    #result1 = io.BytesIO
    db.execute_none('upload_file', {'name': file_name, 'owner_telegram_id': message.from_user.id, 'content': xd, 'size': file_src.file_size, 'created_at': datetime.now()})
    print('uploaded')
    await message.answer('Файл загружен!')
    # await bot.send_message(message.from_user.id, file_name)
    # await bot.send_document(message.from_user.id, document=fail)
@dp.message_handler(commands="get")
async def send_document(message: types.Message):
    """
    Функция, которая принимает пользовательские файлы
    :param message:
    :return nothing:
    """
    logging.info('sending file from server to user')
    file: User_File = db.execute_one('read_file', params={'id': message.text.split(sep=" ")[-1]}, model=User_File)
    #print(bytes(file.content))
    fail = InputFile(filename=file.name, path_or_bytesio=BytesIO(bytes(file.content)))
    await bot.send_document(message.from_user.id, document=fail)


@dp.message_handler(commands="login")
async def login(message: types.Message):
    bot_messages.append(message)
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg=await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте авторизуемся.", reply_markup=keyboard_cancel)
    from_bot_messages.append(msg)
    msg=await message.answer("Пожалуйста, введите ваше имя пользователя.")
    from_bot_messages.append(msg)
    # Переводим пользователя в состояние ожидания имени пользователя
    await Auth.waiting_for_username.set()

@dp.message_handler(commands="register")
async def register(message: types.Message):
    bot_messages.append(message)
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg=await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте зарегистрируемся.", reply_markup=keyboard_cancel)
    from_bot_messages.append(msg)
    msg=await message.answer("Пожалуйста, введите ваше имя пользователя.")
    from_bot_messages.append(msg)
    # Переводим пользователя в состояние ожидания имени пользователя
    await Reg.wait_for_username.set()

@dp.message_handler(commands="cancel", state=[Auth,Reg])
async def cancel(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    # Отправляем сообщение об отмене
    msg=await message.answer("Действие отменено!", reply_markup=keyboard)
    from_bot_messages.append(msg)
    # Завершаем процесс и очищаем хранилище
    await state.finish()


#--------------------------------------------registration--------------------------------------------
@dp.message_handler(state=Reg.wait_for_username)
async def username(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    # Получаем имя пользователя из сообщения
    usr = message.text
    if re.match("^[a-zA-Z0-9_.-]+$", usr) is None:
        msg=await message.answer("В нике обнаружены недопустимые символы. Повторите попытку.")
        from_bot_messages.append(msg)
        await Reg.wait_for_username.set()
        return
    print(type(usr))
    chel: User = db.execute_one('read_user', {'username': usr}, model=User)
    print(chel)
    if chel is not None:
        msg=await message.answer("Это имя уже занято! Попробуйте другое.")
        from_bot_messages.append(msg)
        await Reg.wait_for_username.set()
    else:
        # Сохраняем его во временном хранилище
        await state.update_data(username=usr)
        # Просим ввести пароль
        msg=await message.answer("Пожалуйста, введите ваш пароль.")
        from_bot_messages.append(msg)
        # Переводим пользователя в состояние ожидания пароля
        await Reg.wait_for_password.set()

@dp.message_handler(state=Reg.wait_for_password)
async def password(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    # Получаем имя пользователя из сообщения
    password = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(password=password)
    # Просим ввести пароль
    msg=await message.answer("Пожалуйста, повторите ваш пароль.")
    from_bot_messages.append(msg)
    # Переводим пользователя в состояние ожидания пароля
    await Reg.wait_for_password_2.set()

@dp.message_handler(state=Reg.wait_for_password_2)
async def password_2(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    password = message.text
    await state.update_data(password_2=password)
    data = await state.get_data()
    if data.get('password') == data.get('password_2'):
        try:
            db.execute_none('create_user', {'telegram_id': message.from_user.id,'username': data.get('username'), 'password': data.get('password')})
            msg = await message.answer(f"Поздравляю, {data.get('username')}, Вы зарегистрировались!")
            from_bot_messages.append(msg)
        except Exception as e:
            await message.answer(e)
            print(e)
            msg=await message.answer(f"Что-то пошло не так, {data.get('username')}, обратитесь к админу.")
            from_bot_messages.append(msg)
        await state.finish()
    else:
        msg=await message.answer(f"Пароли не совпадают. Повторите попытку.")
        from_bot_messages.append(msg)
        msg=await message.answer(f"Введите пароль.")
        from_bot_messages.append(msg)
        await Reg.wait_for_password.set()

#-------------------------------------------authorization-------------------------------------------
# Создаем хэндлер для состояния ожидания имени пользователя
@dp.message_handler(state=Auth.waiting_for_username)
async def username(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    # Получаем имя пользователя из сообщения
    usr = message.text
    if re.match("^[a-zA-Z0-9_.-]+$", usr) is None:
        msg=await message.answer("В нике обнаружены недопустимые символы. Повторите попытку.")
        from_bot_messages.append(msg)
        await Auth.waiting_for_username.set()
        return
    # Сохраняем его во временном хранилище
    await state.update_data(username=usr)
    # Просим ввести пароль
    chel: User = db.execute_one('read_user', {'username' : usr}, model=User)
    if chel is None:
        msg=await message.answer("Пользователь не найден. Повторите попытку.")
        from_bot_messages.append(msg)
        await Auth.waiting_for_username.set()
    else:
        msg=await message.answer("Пожалуйста, введите ваш пароль.")
        from_bot_messages.append(msg)
        # Переводим пользователя в состояние ожидания пароля
        await Auth.waiting_for_password.set()

# Создаем хэндлер для состояния ожидания пароля
@dp.message_handler(state=Auth.waiting_for_password)
async def password(message: types.Message, state: FSMContext):
    bot_messages.append(message)
    # Получаем пароль из сообщения
    pswd = message.text
    # Получаем имя пользователя из временного хранилища
    await state.update_data(password=pswd)
    data = await state.get_data()
    #usrnm = data.get("username")
    # Проверяем правильность имени пользователя и пароля (здесь можно использовать свою логику проверки)
    chel: User = db.execute_one('read_user', {'username': data.get('username')}, User)
    print(chel)
    if chel is not None and chel.username == data.get("username") and chel.password == data.get("password"):
        # Если все верно, то отправляем сообщение об успешной авторизации и завершаем процесс
        msg=await message.answer("Поздравляю! Вы успешно авторизовались.")
        from_bot_messages.append(msg)
        await state.finish()
    else:
        # Если что-то не верно, то отправляем сообщение об ошибке и просим повторить попытку
        msg=await message.answer("Неверное имя пользователя или пароль. Пожалуйста, попробуйте еще раз.")
        from_bot_messages.append(msg)
        # Переводим пользователя в состояние ожидания имени пользователя
        await Auth.waiting_for_username.set()

@dp.message_handler()
async def delete_messages(message: types.Message):
    bot_messages.append(message)
    msg = await message.answer("Неопознанное сообщение.", reply_markup=keyboard)
    from_bot_messages.append(msg)


# Запускаем бота
if __name__ == "__main__":
    print('starting...')

    executor.start_polling(dp)