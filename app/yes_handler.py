# another_file.py
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardRemove
from Database.db import Database
from app.answer_button import GroupData

yes_handler_router = Router()
db = Database()

@yes_handler_router.message(F.text == 'Да')
async def yes(message: types.Message):
    chat_id = message.chat.id
    group_name = GroupData.group_name
    if group_name:
        await message.answer(f"Теперь вы будете получать расписание своей группы {group_name}", reply_markup=ReplyKeyboardRemove())
        print("Новый пользователь -", chat_id)
        async with db:
            await db.add_contact(chat_id, group_name)

