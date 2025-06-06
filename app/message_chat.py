from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from Database.db import Database
from create_bot import bot

message_chat_all_router = Router()


class WaitForMessage(StatesGroup):
    waiting = State()

@message_chat_all_router.message(Command("messageAll"))
async def message_chat(message: types.Message, state: FSMContext):

    YOUR_CHAT_ID = 1529963230
    
    if message.chat.id == YOUR_CHAT_ID:
        await state.set_state(WaitForMessage.waiting) 
        await message.reply("Ну давай кобылка, пиши сообщение, оно отправитя всем:")

    else:
        await message.reply("Соси")

@message_chat_all_router.message(WaitForMessage.waiting, F.text)
async def handle_next_message(message: types.Message, state: FSMContext):
    db = Database()
    user_message = message.text
    if user_message == "/stop":
        await message.reply("Щегол")
        await state.clear()
    else:
        await message.reply("Щаааа")
        try:
            async with db:
                group_ids = await db.get_all_group_ids()
                for group in group_ids:
                    chat_id = group["chat_id"]
                    group_name = group["group_name"]

                    try:
                        await bot.send_message(chat_id, user_message)
                        print(f"Сообщение пользователю из {group_name} отправлено в чат {chat_id}.")
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения для группы {group_name}: {e}")            
        except Exception as e:
            print(f"Ошибка при получении данных из базы: {e}")
        await state.clear()
