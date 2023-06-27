from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_keyboard = InlineKeyboardMarkup(row_width=2)
inline_keyboard.add(InlineKeyboardButton('<', callback_data='prev'), InlineKeyboardButton('>', callback_data='next'))
inline_keyboard_next = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('>', callback_data='next'))
inline_keyboard_prev = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('<', callback_data='prev'))