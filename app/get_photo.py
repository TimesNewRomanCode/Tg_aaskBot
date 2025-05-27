import asyncio
from datetime import datetime, time, timedelta
from aiogram import Router, types, F
from Database.db import Database
from pars import download_and_generate_schedule
from create_bot import bot
import os

get_photo_router = Router()


@get_photo_router.message(F.text == '287335')
async def get_photo(message: types.Message = None):
    print("Команда '28733' получена")
    db = Database()
    try:
        start_time = datetime.now()
        async with db:
            group_ids = await db.get_all_group_ids()
            for group in group_ids:
                chat_id = group["chat_id"]
                group_name = group["group_name"]
                #download_and_generate_schedule()
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, "..", "output", f"{group_name}.png")

                # Нормализуем путь (убираем `../`)
                file_path = os.path.normpath(file_path)
                print(file_path)
                try:
                    await bot.send_photo(chat_id, types.FSInputFile(file_path))
                    print(f"Расписание для группы {group_name} отправлено в чат {chat_id}.")
                except Exception as e:
                    print(f"Ошибка при отправке расписания для группы {group_name}: {e}")            
    except Exception as e:
        print(f"Ошибка при получении данных из базы: {e}")
    finally:
        execution_time = datetime.now() - start_time
        print(f"Время выполнения: {execution_time}")  

async def scheduled_task():
    """Задача отправки расписания в определённое время."""
    print("Запуск задачи...")

    target_time = time(20, 30)
    now = datetime.now()
    next_run = datetime.combine(now.date(), target_time)

    print(f"Текущее время: {now}, время запуска: {next_run}")

    if next_run < now:
        next_run = datetime.combine((now + timedelta(days=1)).date(), target_time)

    delay = (next_run - now).total_seconds()
    hours = int(delay//3600)
    minutes = int((delay%3600)//60)
    seconds = int((delay%3600)%60)
    print(f"Задача начнётся через {hours:02}:{minutes:02}:{seconds:02}")

    await asyncio.sleep(delay)

    db = Database()
    download_and_generate_schedule()
    try:
        start_time = datetime.now()
        async with db:
            group_ids = await db.get_all_group_ids()
            for group in group_ids:
                chat_id = group["chat_id"]
                group_name = group["group_name"]
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, "..", "output", f"{group_name}.png")

                # Нормализуем путь (убираем `../`)
                file_path = os.path.normpath(file_path)
                try:
                    await bot.send_photo(chat_id, types.FSInputFile(file_path))
                    
                    print(f"Расписание для группы {group_name} отправлено в чат {chat_id}.")
                except Exception as e:
                    print(f"Ошибка при отправке расписания для группы {group_name}: {e}")
        print(f"Рассылка заняла {general_time}")
    except Exception as e:
        print(f"Ошибка при получении данных из базы: {e}")
    finally:
        execution_time = datetime.now() - start_time
        print(f"Время выполнения: {execution_time}") 


async def run_scheduler():
    """Запуск планировщика."""
    while True:
        await scheduled_task()
