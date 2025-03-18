import asyncio
import logging
from datetime import datetime, time, timedelta
from aiogram import Router, types, F
from Database.db import Database
from parsing import download_and_generate_schedule
from create_bot import bot

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler()]
)

get_photo_router = Router()

@get_photo_router.message(F.text == 'Да1')
async def get_photo(message: types.Message = None):
    """Обработчик команды 'Да1'."""
    logging.info("Команда 'Да1' получена.")
    db = Database()

    try:
        async with db:
            group_ids = await db.get_all_group_ids()
            for group in group_ids:
                chat_id = group["chat_id"]
                group_name = group["group_name"]
                file_path = download_and_generate_schedule(group_name)

                if file_path:
                    try:
                        await bot.send_photo(chat_id, types.FSInputFile(file_path))
                        logging.info(f"Расписание для {group_name} отправлено в чат {chat_id}.")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке расписания для {group_name}: {e}")
    except Exception as e:
        logging.error(f"Ошибка при получении данных из базы: {e}")

async def scheduled_task():
    """Задача отправки расписания в определённое время."""
    logging.info("Запуск задачи расписания.")

    target_time = time(18, 30)
    now = datetime.now()
    next_run = datetime.combine(now.date(), target_time)

    if next_run < now:
        next_run = datetime.combine((now + timedelta(days=1)).date(), target_time)

    delay = (next_run - now).total_seconds()
    logging.info(f"Следующая отправка расписания через {delay} секунд.")

    await asyncio.sleep(delay)

    db = Database()
    try:
        async with db:
            group_ids = await db.get_all_group_ids()
            for group in group_ids:
                chat_id = group["chat_id"]
                group_name = group["group_name"]
                file_path = download_and_generate_schedule(group_name)

                if file_path:
                    try:
                        await bot.send_photo(chat_id, types.FSInputFile(file_path))
                        logging.info(f"Расписание для {group_name} отправлено в чат {chat_id}.")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке расписания для {group_name}: {e}")
    except Exception as e:
        logging.error(f"Ошибка при получении данных из базы: {e}")

async def run_scheduler():
    """Запуск планировщика."""
    while True:
        await scheduled_task()
