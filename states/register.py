from aiogram.dispatcher.filters.state import State, StatesGroup

class Reg(StatesGroup):
    wait_for_username = State()
    wait_for_password = State()
    wait_for_password_2 = State()