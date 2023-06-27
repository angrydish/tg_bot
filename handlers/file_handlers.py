from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from datetime import datetime
import logging

from io import BytesIO

from db.db_connect import db
from models.models import User_File
from states.auth import Auth
from keyboards.kb_authorized import keyboard_authorized
from app.bot import bot

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
    if file_name is None or file_name == "":
        if message.content_type == "video":
            file_name = "video_"+datetime.now().strftime("%d-%m-%Y-%H:%M:%S")+".mp4"
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


async def get_document(message: types.Message, state: FSMContext):
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

def register_file_handlers(dp: Dispatcher):
    dp.register_message_handler(document_sent_by_user, state = Auth.logged_in, content_types = ['document', 'audio', 'video'])
    dp.register_message_handler(get_document, commands = "get", state = Auth.logged_in)
