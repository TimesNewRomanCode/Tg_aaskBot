# app/answer_button.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.keyboards_Reply import verification

answer_button_router = Router()

class GroupData:
    group_name = None

@answer_button_router.callback_query(F.data.startswith('btn_'))
async def process_order_callback(callback_query: CallbackQuery):
    GroupData.group_name = callback_query.data.split('_')[1]
    await callback_query.message.answer(f"Ваша группа {GroupData.group_name}?", reply_markup=verification())
    await callback_query.answer()

