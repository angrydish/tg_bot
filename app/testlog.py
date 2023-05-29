# Импортируем необходимые модули
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')
# Создаем бота и диспетчера с токеном и хранилищем состояний

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
    username = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(username=username)
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
        await message.answer(f"Поздравляю, {data.get('username')}, Вы зарегистрировались!")
    else:
        await message.answer(f"Пароли не совпадают. Повторите попытку.")
        await message.answer(f"Введите пароль.")
        await Reg.wait_for_password.set()

#-------------------------------------------authorization-------------------------------------------
# Создаем хэндлер для состояния ожидания имени пользователя
@dp.message_handler(state=Auth.waiting_for_username)
async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    username = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(username=username)
    # Просим ввести пароль
    await message.answer("Пожалуйста, введите ваш пароль.")
    # Переводим пользователя в состояние ожидания пароля
    await Auth.waiting_for_password.set()

# Создаем хэндлер для состояния ожидания пароля
@dp.message_handler(state=Auth.waiting_for_password)
async def password(message: types.Message, state: FSMContext):
    # Получаем пароль из сообщения
    password = message.text
    # Получаем имя пользователя из временного хранилища
    data = await state.get_data()
    username = data.get("username")
    # Проверяем правильность имени пользователя и пароля (здесь можно использовать свою логику проверки)
    if username == "admin" and password == "1234":
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
    executor.start_polling(dp)