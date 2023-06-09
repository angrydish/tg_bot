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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Chat, ContentTypes, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from app.security import sha256, check_sha256_password

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
    'host': host,
    'port': port,
    'database': database,
    'user': user,
    'password': password})
print(db.execute_one('test_query'))
try:
    db.execute_none('create_database')
except BaseException as e:
    print("----------")
    print("if you see this message, then db tried to die, but all went good, error:")
    print(e)
    print("as i said it did")
    print("----------")

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("/login"))
keyboard.add(KeyboardButton("/register"))
#keyboard.add(KeyboardButton("/delete"))

keyboard_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_cancel.add("/cancel")

keyboard_authorized = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_authorized.add(KeyboardButton("/list"))
keyboard_authorized.add(KeyboardButton("/sort"))
keyboard_authorized.add(KeyboardButton("/get"))
keyboard_authorized.add(KeyboardButton("/search"))

# Определяем класс состояний для авторизации
class Auth(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    logged_in = State()


class Reg(StatesGroup):
    wait_for_username = State()
    wait_for_password = State()
    wait_for_password_2 = State()


# Создаем хэндлер для команды /start, которая запускает процесс авторизации


@dp.message_handler(state=Auth.logged_in, content_types=['document', 'audio', 'video'])
async def document_sent_by_user(message: types.Message, state: FSMContext):
    """
    Функция, которая принимает пользовательские файлы
    :param state:
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
    data = await state.get_data()
    logging.info('uploading file to server')
    file_name = file_src.file_name
    print(file_name)
    print(message.content_type)
    print(file_src)
    # print(message.audio.)
    # result = await bot.download_file_by_id(message.audio.file_id)
    # fail = InputFile(filename=file_name, path_or_bytesio=BytesIO(bytes(result.read()))) # получили файл, можно загрузить в бд

    await message.answer('Начал загрузку файла на сервер.')
    print('1st stage')
    file = await bot.get_file(file_src.file_id)
    print('2nd stage')
    file = await bot.download_file(file.file_path)
    xd = bytes.fromhex(file.read().hex())

    print('uploading')
    # result1 = io.BytesIO
    db.execute_none('upload_file',
                    {'name': file_name, 'owner_user_id': data.get('user_id'), 'owner_telegram_id': message.from_user.id, 'content': xd,
                     'size': file_src.file_size, 'created_at': datetime.now()})
    print('uploaded')
    await message.answer(f'Файл {file_name} загружен!', reply_markup=keyboard_authorized)
    # await bot.send_message(message.from_user.id, file_name)
    # await bot.send_document(message.from_user.id, document=fail)




@dp.message_handler(commands="start")
async def login(message: types.Message):
    a = message.date
    b = datetime.now()
    print(a, b, sep="\n")
    print(b - a)
    print(f"start requested by {message.from_user.username}")
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg = await message.answer(f"""
    Приветствую, {message.from_user.username}. 
    
    Я - бот, который умеет хранить твои файлы.
    
    В любой момент ты можешь получить доступ к необходимому тебе файлу, и тебе не придется листать историю, чтобы найти что-то нужное.
    """, reply_markup=keyboard)
    # Переводим пользователя в состояние ожидания имени пользователя


@dp.message_handler(commands="delete", state=Auth.logged_in)
async def send_document(message: types.Message, state: FSMContext):
    """
    Функция, которая принимает пользовательские файлы
    :param state:
    :param message:
    :return nothing:
    """
    args = message.text.split(sep=" ")
    print(args)
    data = await state.get_data()
    if len(args) == 2 and args[1].isdigit():
        infa: User_File = db.execute_one('check_file_owner', {'file_id': args[1]}, model=User_File)
        if infa is not None and data.get('user_id') == infa.owner_user_id:
            await message.answer("Удаление файла. Подождите...")
            db.execute_none('delete_file', params={'id': args[1]})
            await message.answer("Файл удален.")
        else:
            await message.answer("аяяй низя так делать")
    else:
        await message.answer("Введите число. Пример: /delete 1.")



@dp.message_handler(commands="get", state=Auth.logged_in)
async def send_document(message: types.Message, state: FSMContext):
    """
    Функция, которая принимает пользовательские файлы
    :param state:
    :param message:
    :return nothing:
    """
    args = message.text.split(sep=" ")
    print(args)
    data = await state.get_data()
    if len(args) == 2 and args[1].isdigit():
        infa: User_File = db.execute_one('check_file_owner', {'file_id': args[1]}, model=User_File)
        if infa is not None and data.get('user_id') == infa.owner_user_id:
            logging.info('sending file from server to user')
            await message.answer("Подготовка файла. Подождите...")
            file: User_File = db.execute_one('read_file', params={'id': args[1]}, model=User_File)
            # print(bytes(file.content))
            fail = InputFile(filename=file.name, path_or_bytesio=BytesIO(bytes(file.content)))
            await message.answer("Отправляю файл...")
            await bot.send_document(message.from_user.id, document=fail)
        else:
            await message.answer("аяяй низя так делать")
    else:
        await message.answer("Введите число. Пример: /get 1.")

@dp.message_handler(commands="cancel", state=[Auth.waiting_for_username, Auth.waiting_for_password, Reg])
async def cancel(message: types.Message, state: FSMContext):
    # Отправляем сообщение об отмене
    msg = await message.answer("Действие отменено!", reply_markup=keyboard)

    # Завершаем процесс и очищаем хранилище
    await state.finish()


# --------------------------------------------registration-begin------------------------------------------
@dp.message_handler(commands="register")
async def register(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg = await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте зарегистрируемся.",
                               reply_markup=keyboard_cancel)
    msg = await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Reg.wait_for_username.set()
@dp.message_handler(state=Reg.wait_for_username)
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


@dp.message_handler(state=Reg.wait_for_password)
async def password(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    password = message.text
    # Сохраняем его во временном хранилище
    await state.update_data(password=password)
    # Просим ввести пароль
    msg = await message.answer("Пожалуйста, повторите ваш пароль.")
    # Переводим пользователя в состояние ожидания пароля
    await Reg.wait_for_password_2.set()


@dp.message_handler(state=Reg.wait_for_password_2)
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
# --------------------------------------------registration-end------------------------------------------

# -------------------------------------------authorization-begin-----------------------------------------
@dp.message_handler(commands="login")
async def login(message: types.Message):
    # Отправляем приветственное сообщение и просим ввести имя пользователя
    msg = await message.answer("Привет! Добро пожаловать в мой бот. Для начала давайте авторизуемся.",
                               reply_markup=keyboard_cancel)
    msg = await message.answer("Пожалуйста, введите ваше имя пользователя.")
    # Переводим пользователя в состояние ожидания имени пользователя
    await Auth.waiting_for_username.set()
# Создаем хэндлер для состояния ожидания имени пользователя
@dp.message_handler(state=Auth.waiting_for_username)
async def username(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из сообщения
    usr = message.text
    if re.match("^[a-zA-Z0-9_.-]+$", usr) is None:
        msg = await message.answer("В нике обнаружены недопустимые символы. Повторите попытку.")
        await Auth.waiting_for_username.set()
        return
    # Сохраняем его во временном хранилище
    await state.update_data(username=usr)
    # Просим ввести пароль
    chel: User = db.execute_one('read_user', {'username': usr}, model=User)
    if chel is None:
        msg = await message.answer("Пользователь не найден. Повторите попытку.")
        await Auth.waiting_for_username.set()
    else:
        msg = await message.answer("Пожалуйста, введите ваш пароль.")
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
    # usrnm = data.get("username")
    # Проверяем правильность имени пользователя и пароля (здесь можно использовать свою логику проверки)
    chel: User = db.execute_one('read_user', {'username': data.get('username')}, User)
    print(chel)
    if chel is not None and chel.username == data.get("username") and chel.password == sha256(data.get("password")):
        # Если все верно, то отправляем сообщение об успешной авторизации и завершаем процесс
        msg = await message.answer("Поздравляю! Вы успешно авторизовались.", reply_markup=keyboard_authorized)
        await state.update_data(user_id=chel.id)
        data = await state.get_data()
        print(data)
        await Auth.logged_in.set()
    else:
        # Если что-то не верно, то отправляем сообщение об ошибке и просим повторить попытку
        msg = await message.answer("Неверное имя пользователя или пароль. Пожалуйста, попробуйте еще раз.")
        # Переводим пользователя в состояние ожидания имени пользователя
        await Auth.waiting_for_username.set()


# -------------------------------------------authorization-end-----------------------------------------

inline_keyboard = InlineKeyboardMarkup(row_width=2)
inline_keyboard.add(InlineKeyboardButton('<', callback_data='prev'), InlineKeyboardButton('>', callback_data='next'))
inline_keyboard_next = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('>', callback_data='next'))
inline_keyboard_prev = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('<', callback_data='prev'))
@dp.callback_query_handler(lambda c: c.data, state=Auth.logged_in)
async def process_callback_kb1btn1(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    message = callback_query.message
    data = await state.get_data()
    #await bot.answer_callback_query(callback_query.id, text='abcdefg')
    #print(code)
    print(f'pages: {data.get("pages")}')
    current_page = data.get('current_page')
    if code == "next":
        current_page += 1
        if current_page != data.get("pages"):
            await state.update_data(current_page=current_page)
            text, xd = await get_output(callback_query.message, state, data.get('files_list'))
            await bot.edit_message_text(message_id=callback_query.message.message_id, chat_id=callback_query.message.chat.id, text=text)
            await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                                reply_markup=inline_keyboard)
            print(1)
        elif current_page == data.get('pages'):
            await state.update_data(current_page=current_page)
            text, xd = await get_output(callback_query.message, state, data.get('files_list'))
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.message.chat.id, text=text)
            await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                                reply_markup=inline_keyboard_prev)
            print(2)

    elif code == "prev":
        current_page -= 1
        if current_page != 1:
            await state.update_data(current_page=current_page)
            text, xd = await get_output(callback_query.message, state, data.get('files_list'))
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.message.chat.id, text=text)
            await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                                reply_markup=inline_keyboard)
            print(3)
        elif current_page == 1:
            await state.update_data(current_page=current_page)
            text, xd = await get_output(callback_query.message, state, data.get('files_list'))
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.message.chat.id, text=text)
            await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                                reply_markup=inline_keyboard_next)
            print(4)

    print(f'current_page: {current_page}')

    #await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')

async def get_output(message: types.Message, state: FSMContext, files_list: list):
    #files: User_File = db.execute_all('read_all_files_without_content',params={'owner_user_id': message.from_user.id} , model=User_File)
    if len(files_list) % 10 != 0:
        pages = (len(files_list) // 10) + 1
    else:
        pages = (len(files_list) // 10)
    data = await state.get_data()
    current_page = data.get('current_page')
    await state.update_data(pages=pages, files_list=files_list)
    print(current_page)
    output_message = ""
    left_border = data.get('current_page') * 10 - 10
    right_border = (data.get('current_page') * 10, len(files_list) )[current_page * 10 > len(files_list)]
    print(f'len_files: {len(files_list)}, current_page: {current_page}, pages: {pages}, left: {left_border}, right: {right_border}')
    print(right_border)
    for i in range(left_border, right_border):
        #print(files_list[i])
        #print(i)
        output_message += files_list[i]
    return output_message, pages


async def print_with_pages(message: types.Message, state: FSMContext, files_list: list):
    #files: User_File = db.execute_all('read_all_files_without_content',params={'owner_user_id': message.from_user.id} , model=User_File)
    output_message, pages = await get_output(message, state, files_list)
    await state.update_data(output_message=output_message)
    #print(output_message)
    if pages > 1:
        await message.answer(output_message, reply_markup=inline_keyboard_next)
    else:
        await message.answer(output_message)



@dp.message_handler(commands="sort", state=Auth.logged_in)
async def send_document(message: types.Message, state: FSMContext):
    args = message.text.split(sep=" ")
    await state.update_data(current_page=1)
    data = await state.get_data()
    files: list[User_File] = db.execute_all('sort_by_size', params={'owner_user_id': data.get('user_id')}, model=User_File)
    print(f'files: {files}')
    if len(files) != 0:
        output_message=[]
        for file in files:
            output_message.append(f"""
Файл №{file.id}
    Имя: {file.name}
    Размер: {file.size / 1024 / 1024} мегабайт
    Создан: {file.created_at}
    Чтобы скачать, введите /get {file.id}
            """)
        await print_with_pages(message, state, output_message)

    else:
        await message.answer("Возможно, у вас еще нет файлов!")

@dp.message_handler(commands="search", state=Auth.logged_in)
async def send_document(message: types.Message, state: FSMContext):
    args = message.text.split(sep=" ")
    await state.update_data(current_page=1)
    if len(args) != 2:
        await message.answer("Использование:\n/search <имя файла>")
        return
    args[1]+='%'
    print(args)

    data = await state.get_data()
    files: list[User_File] = db.execute_all('search_file_by_string', params={'string': args[1], 'owner_user_id': data.get('user_id')},model=User_File)
    print(f'files: {files}')
    if len(files) != 0:
        output_message=[]
        for file in files:
            output_message.append(f"""
Файл №{file.id}
    Имя: {file.name}
    Размер: {file.size / 1024 / 1024} мегабайт
    Создан: {file.created_at}
    Чтобы скачать, введите /get {file.id}
            """)
        await print_with_pages(message, state, output_message)

    else:
        await message.answer("По вашему запросу ничего не найдено!")

@dp.message_handler(state=Auth.logged_in, commands="list")
async def user_logged_in(message: types.Message, state: FSMContext):
    await state.update_data(current_page=1)
    data = await state.get_data()
    print(data.get('user_id'))
    await message.answer("Получаю список файлов...")
    all_files: list[User_File] = db.execute_all('read_all_files_without_content', {'owner_user_id': data.get('user_id')}, model=User_File)
    await message.reply("Список доступных файлов:")
    output_message = []
    for file in all_files:
        output_message.append(f"""
        
Файл №{file.id}
    Имя: {file.name}
    Размер: {file.size / 1024 / 1024 } мегабайт
    Создан: {file.created_at}
    Чтобы скачать, введите /get {file.id}
""")
    if output_message:
        #await message.answer(output_message, reply_markup=inline_keyboard)
        await print_with_pages(message, state, output_message)
    else:
        await message.answer("У вас еще нет файлов. Вы можете их загрузить, просто выбрав меню загрузки файлов.")

@dp.message_handler(state=Auth.logged_in, commands="logout")
async def user_logout(message: types.Message, state: FSMContext):
    await message.answer("Вы вышли из пользователя.", reply_markup=keyboard)
    await state.finish()



@dp.message_handler()
async def delete_messages(message: types.Message):
    await message.answer("Неопознанное сообщение.", reply_markup=keyboard)


# Запускаем бота
if __name__ == "__main__":
    print('starting...')
    executor.start_polling(dp)
