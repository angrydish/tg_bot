from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from datetime import datetime

from db.db_connect import db
from models.models import User_File
from states.auth import Auth
from states.register import Reg
from keyboards.kb_start import keyboard
from keyboards.kb_inline_list import inline_keyboard, inline_keyboard_next, inline_keyboard_prev
from app.bot import bot

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
        await message.answer(output_message, reply_markup=inline_keyboard_next, parse_mode="HTML")
    else:
        await message.answer(output_message)


async def start(message: types.Message):
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

async def delete_document(message: types.Message, state: FSMContext):
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


async def list_files(message: types.Message, state: FSMContext):
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



async def search_file(message: types.Message, state: FSMContext):
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

async def sort_files(message: types.Message, state: FSMContext):
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


async def cancel(message: types.Message, state: FSMContext):
    # Отправляем сообщение об отмене
    await message.answer("Действие отменено!", reply_markup=keyboard)

    # Завершаем процесс и очищаем хранилище
    await state.finish()

async def user_logout(message: types.Message, state: FSMContext):
    await message.answer("Вы вышли из пользователя.", reply_markup=keyboard)
    await state.finish()


def misc_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, commands = "cancel", state = [Auth.waiting_for_username, Auth.waiting_for_password, Reg])
    dp.register_message_handler(start, commands = "start", state = None)
    dp.register_message_handler(user_logout, commands = "logout", state = Auth.logged_in)
    dp.register_message_handler(sort_files, commands = "sort", state = Auth.logged_in)
    dp.register_message_handler(search_file, commands = "search", state = Auth.logged_in)
    dp.register_message_handler(list_files, commands = "list", state = Auth.logged_in)
    dp.register_message_handler(delete_document, commands = "delete", state = Auth.logged_in)
    dp.register_callback_query_handler(process_callback_kb1btn1, state = Auth.logged_in)
