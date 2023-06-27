from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_authorized = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_authorized.add(KeyboardButton("/list"))
keyboard_authorized.add(KeyboardButton("/sort"))
keyboard_authorized.add(KeyboardButton("/search"))
keyboard_authorized.add(KeyboardButton("/get"))
keyboard_authorized.add(KeyboardButton("/delete"))
keyboard_authorized.add(KeyboardButton("/logout"))