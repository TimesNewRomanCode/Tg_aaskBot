from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardRemove
from Database.db import Database
from aiogram.fsm.context import FSMContext
from datetime import datetime

yes_handler_router = Router()
db = Database()

@yes_handler_router.message(F.text == 'Да')
async def yes(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    data = await state.get_data()
    group_name = data.get("group_name")
    username = message.from_user.username
    date_registr = datetime.now()
    if group_name:
        async with db:
            await db.add_contact(chat_id, group_name, username, date_registr)

        await message.answer(f"Теперь вы будете получать расписание своей группы {group_name}", reply_markup=ReplyKeyboardRemove())