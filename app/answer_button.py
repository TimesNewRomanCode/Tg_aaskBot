from aiogram import Router, F,  types
from aiogram.types import CallbackQuery
from keyboards.keyboards_Reply import verification
from aiogram.fsm.context import FSMContext

answer_button_router = Router()

@answer_button_router.callback_query(F.data.startswith('btn_'))
async def process_order_callback(callback_query: CallbackQuery, state: FSMContext):
    group_name = callback_query.data.split('_')[1]
    await state.set_data({"group_name": group_name})
    await callback_query.message.answer(f"Ваша группа {group_name}?", reply_markup=verification())
    await callback_query.answer()

