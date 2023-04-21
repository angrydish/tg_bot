import time
import logging
import requests
import json
import os
import typing

from aiogram import Bot, Dispatcher, executor, types
from selenium import webdriver
from selenium.webdriver.common.by import By
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ContentTypes, InputFile
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN_TG_BOT')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

text = """
Тестовый текст
для многострочного сообщения
ага, а вот здесь {} имя пользователя

а тут твое сообщение:
{}
"""

class Form(StatesGroup):
    choice = State()  # Will be represented in storage as 'Form:name'

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    # await message.reply(f'Privet, {user_full_name}') - ответ на сообщение
    # for i in range(1):
    # time.sleep(2)
    await bot.send_message(user_id, text.format(message.from_user.username, message.text))  # прислать сообщение


@dp.message_handler(commands=['ftjgvnyhfhcjtgvytgyhjfrtgyhrffjtgyhrtghfyrtghfyj'])
async def get_zapros(message: types.Message):
    myacc_csgo = requests.get("https://steamcommunity.com/inventory/76561198259026080/730/2?l=russian&count=1000")
    dict = json.loads(myacc_csgo.text)
    logging.info(f'wants steam {time.asctime()} {message.from_user.username}')
    otvet = f"""
    {myacc_csgo}

    {dict}
    """
    await bot.send_message(message.from_user.id, otvet)

@dp.message_handler(content_types=ContentTypes.DOCUMENT)
async def unknown_message(message: types.Message):
    logging.info(f'uploading file to server')
    file_name = message.document.file_name
    #my_file = open(file_name, "w+")
    print(message.document)
    result = await bot.download_file_by_id(message.document.file_id)
    #print(result)
    #print(bytes(result.read()))
    #fail = InputFile(filename="aboba", path_or_bytesio=result)
    #print(fail)
    result = bytes(result.read())
    #print(result)
    #await bot.download_file('.')
    #typing.BinaryIO
    #my_file.write(message.document)
    #my_file.close()
    await bot.send_message(message.from_user.id, file_name)
    #await bot.send_file(message.document.mime_type,file=result)
    #await bot.send_document(message.from_user.id, document=InputFile(filename=message.document.file_name, path_or_bytesio=await bot.download_file_by_id(message.document.file_id)))
    await bot.send_document(message.from_user.id, document=result)



@dp.message_handler(commands=['bot_ip'])
async def get_ip(message: types.Message):
    my_ip = requests.get("http://api.myip.com")
    logging.info(f'wants ip {time.asctime()} {message.from_user.username}')
    print(my_ip.text)
    await bot.send_message(message.from_user.id, my_ip.text)

if __name__ == '__main__':
    print('bebra')
    executor.start_polling(dp)
