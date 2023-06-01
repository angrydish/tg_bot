# Импортируем необходимые модули
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
import os
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
# Определяем класс состояний для авторизации
class Auth(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class Reg(StatesGroup):
    wait_for_username = State()
    wait_for_password = State()
    wait_for_password_2 = State()


# Создаем хэндлер для команды /start, которая запускает процесс авторизации
@dp.message_handler(commands="login")
async def login(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте авторизуемся.")
    await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Auth.waiting_for_username.set()

@dp.message_handler(commands="register")
async def register(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте зарегистрируемся.")
    await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Reg.wait_for_username.set()

@dp.message_handler(commands="cancel", state=[Auth,Reg])
async def cancel(message: types.Message, state: FSMContext):
    # Отправляем сообщение об отмене
    await message.answer("Действие отменено!")
    # Завершаем процесс и очищаем хранилище
    await state.finish()


#--------------------------------------------registration--------------------------------------------
@dp.message_handler(state=Reg.wait_for_username)
async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    usr = message.text
    print(type(usr))
    chel: User = db.execute_one('read_user', {'username': usr}, model=User)
    print(chel)
    if chel is not None:
        await message.answer("Это имя уже занято! Попробуйте другое.")
        await Reg.wait_for_username.set()
    else:
        # Сохраняем его во временном хранилище
        await state.update_data(username=usr)
        # Просим ввести пароль
        await message.answer("Пожалуйста, введите ваш пароль.")
        # Переводим пользователя в состояние ожидания пароля
        await Reg.wait_for_password.set()

@dp.message_handler(state=Reg.wait_for_password)
async def password(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    password = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(password=password)
    # Просим ввести пароль
    await message.answer("Пожалуйста, повторите ваш пароль.")
    # Переводим пользователя в состояние ожидания пароля
    await Reg.wait_for_password_2.set()

@dp.message_handler(state=Reg.wait_for_password_2)
async def password_2(message: types.Message, state: FSMContext):
    password = message.text
    await state.update_data(password_2=password)
    data = await state.get_data()
    if data.get('password') == data.get('password_2'):
        db.execute_none('create_user', {'username': data.get('username'), 'password': data.get('password')})
        await message.answer(f"Поздравляю, {data.get('username')}, Вы зарегистрировались!")
        await state.finish()
    else:
        await message.answer(f"Пароли не совпадают. Повторите попытку.")
        await message.answer(f"Введите пароль.")
        await Reg.wait_for_password.set()

#-------------------------------------------authorization-------------------------------------------
# Создаем хэндлер для состояния ожидания имени пользователя
@dp.message_handler(state=Auth.waiting_for_username)
async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    usr = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(username=usr)
    # Просим ввести пароль
    chel: User = db.execute_one('read_user', {'username' : usr}, model=User)
    if chel is None:
        await message.answer("Пользователь не найден. Повторите попытку.")
        await Auth.waiting_for_username.set()
    else:
        await message.answer("Пожалуйста, введите ваш пароль.")
        # Переводим пользователя в состояние ожидания пароля
        await Auth.waiting_for_password.set()

# Создаем хэндлер для состояния ожидания пароля
@dp.message_handler(state=Auth.waiting_for_password)
async def password(message: types.Message, state: FSMContext):
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
        await message.answer("Поздравляю! Вы успешно авторизовались.")
        await state.finish()
    else:
        # Если что-то не верно, то отправляем сообщение об ошибке и просим повторить попытку
        await message.answer("Неверное имя пользователя или пароль. Пожалуйста, попробуйте еще раз.")
        # Переводим пользователя в состояние ожидания имени пользователя
        await Auth.waiting_for_username.set()




# Запускаем бота
if __name__ == "__main__":
    print('starting...')
    executor.start_polling(dp)