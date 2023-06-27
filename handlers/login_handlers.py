from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import re

from db.db_connect import db
from models.models import User
from app.security import sha256
from states.auth import Auth
from keyboards.kb_auth import *
from keyboards.kb_authorized import *


async def login(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте авторизуемся.",
                               reply_markup=keyboard_cancel)
    await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Auth.waiting_for_username.set()
    
# Создаем хэндлер для состояния ожидания имени пользователя


async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    usr = message.text
    if re.match("^[a-zA-Z0-9_.-]+$", usr) is None:
        await message.answer("В нике обнаружены недопустимые символы. Повторите попытку.")
        await Auth.waiting_for_username.set()
        return
    # Сохраняем его во временном хранилище
    await state.update_data(username=usr)
    # Просим ввести пароль
    chel: User = db.execute_one('read_user', {'username': usr}, model=User)
    if chel is None:
        await message.answer("Пользователь не найден. Повторите попытку.")
        await Auth.waiting_for_username.set()
    else:
        await message.answer("Пожалуйста, введите ваш пароль.")
        # Переводим пользователя в состояние ожидания пароля
        await Auth.waiting_for_password.set()


# Создаем хэндлер для состояния ожидания пароля
async def password(message: types.Message, state: FSMContext):
    # Получаем пароль из сообщения
    pswd = message.text
    # Получаем имя пользователя из временного хранилища
    await state.update_data(password=pswd)
    data = await state.get_data()
    # usrnm = data.get("username")
    # Проверяем правильность имени пользователя и пароля (здесь можно использовать свою логику проверки)
    chel: User = db.execute_one('read_user', {'username': data.get('username')}, User)
    print(chel)
    if chel is not None and chel.username == data.get("username") and chel.password == sha256(data.get("password")):
        # Если все верно, то отправляем сообщение об успешной авторизации и завершаем процесс
        await message.answer("Поздравляю! Вы успешно авторизовались.", reply_markup=keyboard_authorized)
        await state.update_data(user_id=chel.id)
        data = await state.get_data()
        print(data)
        await Auth.logged_in.set()
    else:
        # Если что-то не верно, то отправляем сообщение об ошибке и просим повторить попытку
        await message.answer("Неверное имя пользователя или пароль. Пожалуйста, попробуйте еще раз.")
        # Переводим пользователя в состояние ожидания имени пользователя
        await Auth.waiting_for_username.set()

def authorization(dp: Dispatcher):
    dp.register_message_handler(login,commands="login", state=None)
    dp.register_message_handler(username, state=Auth.waiting_for_username)
    dp.register_message_handler(password, state=Auth.waiting_for_password)
