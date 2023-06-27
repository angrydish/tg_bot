from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import re

from db.db_connect import db
from models.models import *
from app.security import sha256
from states.register import Reg
from states.auth import Auth
from keyboards.kb_auth import *
from keyboards.kb_authorized import *
from keyboards.kb_start import keyboard


async def register(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg = await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте зарегистрируемся.",
                               reply_markup=keyboard_cancel)
    msg = await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Reg.wait_for_username.set()

async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    usr = message.text
    if re.match("^[a-zA-Z0-9_.-]+$", usr) is None:
        msg = await message.answer("В нике обнаружены недопустимые символы. Повторите попытку.")
        await Reg.wait_for_username.set()
        return
    print(type(usr))
    chel: User = db.execute_one('read_user', {'username': usr}, model=User)
    print(chel)
    if chel is not None:
        msg = await message.answer("Это имя уже занято! Попробуйте другое.")
        await Reg.wait_for_username.set()
    else:
        # Сохраняем его во временном хранилище
        await state.update_data(username=usr)
        # Просим ввести пароль
        msg = await message.answer("Пожалуйста, введите ваш пароль.")
        # Переводим пользователя в состояние ожидания пароля
        await Reg.wait_for_password.set()


async def password(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    password = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(password=password)
    # Просим ввести пароль
    msg = await message.answer("Пожалуйста, повторите ваш пароль.")
    # Переводим пользователя в состояние ожидания пароля
    await Reg.wait_for_password_2.set()


async def password_2(message: types.Message, state: FSMContext):
    password = message.text
    await state.update_data(password_2=password)
    data = await state.get_data()
    if data.get('password') == data.get('password_2'):
        try:
            db.execute_none('create_user', {'telegram_id': message.from_user.id, 'username': data.get('username'),
                                            'password': sha256(data.get('password'))})
            msg = await message.answer(f"Поздравляю, {data.get('username')}, Вы зарегистрировались!", reply_markup=keyboard_authorized)
            chel: User = db.execute_one('read_user', {'username': data.get('username')}, model=User)
            await state.update_data(user_id=chel.id)
            await Auth.logged_in.set()
        except Exception as e:
            await message.answer(e)
            print(e)
            msg = await message.answer(f"Что-то пошло не так, {data.get('username')}, обратитесь к админу.")
            await state.finish()
    else:
        msg = await message.answer(f"Пароли не совпадают. Повторите попытку.")
        msg = await message.answer(f"Введите пароль.")
        await Reg.wait_for_password.set()

async def unknown_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Неопознанное сообщение.", reply_markup=keyboard)
    elif current_state == "Auth:logged_in":
        await message.answer("Неопознанное сообщение.", reply_markup=keyboard_authorized)

def registration(dp: Dispatcher):
    dp.register_message_handler(register, commands="register", state=None)
    dp.register_message_handler(username, state=Reg.wait_for_username)
    dp.register_message_handler(password, state=Reg.wait_for_password)
    dp.register_message_handler(password_2, state=Reg.wait_for_password_2)
    dp.register_message_handler(unknown_message, state=[Auth, Reg, None])