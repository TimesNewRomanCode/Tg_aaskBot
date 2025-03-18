from aiogram import Router, F, types
from aiogram.filters import CommandStart
import keyboards.keyboards_Inline as kb

start_router = Router()

@start_router.message(CommandStart())
async def message_handler(message: types.Message):
    await message.reply("Из какой вы группы?", reply_markup=kb.inline_kb1)


