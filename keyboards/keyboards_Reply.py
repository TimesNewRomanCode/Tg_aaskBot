from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

def verification():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Да', callback_data=''),
                KeyboardButton(text='Нет', callback_data='')
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder='Это точно ваша группа?'
)