from aiogram.dispatcher.filters.state import State, StatesGroup

class Auth(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    logged_in = State()