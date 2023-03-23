import time
import logging
import requests
import json


from aiogram import Bot, Dispatcher, executor, types
from selenium import webdriver
from selenium.webdriver.common.by import By


TOKEN =


bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


text = """
Тестовый текст
для многострочного сообщения
ага, а вот здесь {} имя пользователя

а тут твое сообщение:
{}
"""

def function():
    browser = webdriver.Chrome()
    browser.get("https://coinmarketcap.com/")

    for i in range(8):
        browser.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    block = browser.find_element(By.TAG_NAME, 'tbody')
    table_data_list = block.text.split("\n")

    dict = []
    banned_indeces = [4, 6, 7, 8]
    banned = []

    for ind in banned_indeces:
        banned += [i for i in range(ind, len(table_data_list), 9)]

    newMassiv = [data for data in table_data_list if table_data_list.index(
        data) not in banned]
    for i in range(0, len(newMassiv), 5):
        dict.append({})

    for j, i in zip(range(100), range(0, len(newMassiv), 5)):
        dict[j]['id'] = newMassiv[i]
        dict[j]['coin'] = {}
        dict[j]['coin']['NAME'] = newMassiv[i + 1]
        dict[j]['coin']['SYMBOL'] = newMassiv[i + 2]
        dict[j]['coin']['PRICE'] = newMassiv[i + 3]
        dict[j]['coin']['MARKET_CAP'] = newMassiv[i + 4]
    return dict

    # with open("E:\code\SelParse\SPJ.json", "w", encoding="utf-8") as file:
    #     json.dump(dict, file, indent=4, ensure_ascii=False)
    # print("Script succesfully complete!")



@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    logging.info(f'{time.asctime()} {user_id=} {user_full_name=} {user_username=}\nmessage:"{message.text}" \n')
    #await message.reply(f'Privet, {user_full_name}') - ответ на сообщение
    #for i in range(1):
        #time.sleep(2)
    await bot.send_message(user_id, text.format(message.from_user.username, message.text)) # прислать сообщение


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


@dp.message_handler(commands=['bot_ip'])
async def get_ip(message: types.Message):
    my_ip=requests.get("http://api.myip.com")
    logging.info(f'wants ip {time.asctime()} {message.from_user.username}')
    await bot.send_message(message.from_user.id, json.loads(my_ip.text))


@dp.message_handler(commands=['market'])
async def get_crypto(message: types.Message):
    logging.info(f'wants get crypto data {time.asctime()} {message.from_user.username}')
    await message.reply(f'{message.from_user.username}, вот список криптовалют в JSON формате:\n{function()}')




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print('bebra')
    executor.start_polling(dp)

