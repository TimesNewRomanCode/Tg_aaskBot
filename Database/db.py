import asyncpg
import os
import logging
from dotenv import load_dotenv
from datetime import datetime 

load_dotenv()

logger = logging.getLogger(__name__)

GROUP_NAMES = [
    "А-21", "А-31", "А-41", "А-42", "ГД-31", "ГД-32", "ГД-41", "ГД-42",
    "Д-11", "Д-12", "Д-21", "Д-22", "Д-31", "Д-32", "Д-41", "Д-42",
    "ЗИО-21", "ЗИО-22", "ЗУ-31", "ЗУ-32", "ЗУ-41", "ЗУ-42", "ИСиП-21",
    "ИСиП-31", "ИСиП-41", "ИСиП-42", "ИСиСС-11", "МСГ-11", "МСГ-12",
    "МСГ-21", "МСГ-31", "МСГ-32", "МСГ-41", "МСГ-42", "МСТУ-11", "МСТУ-21",
    "МСТУ-31", "МСТУ-41", "ПНСК-11", "ПНСК-21", "ПНСК-31", "ПНСК-32",
    "ПНСК-41", "ПНСК-42", "ССА-11", "ССА-21", "СЭГПС-11", "СЭГПС-21",
    "СЭГПС-31", "СЭГПС-41", "СЭЗС-11", "СЭЗС-12", "СЭЗС-21", "СЭЗС-22",
    "СЭЗС-23", "СЭЗС-31", "СЭЗС-32", "СЭЗС-33", "СЭЗС-34", "СЭЗС-41",
    "СЭЗС-42", "СЭЗС-43", "СЭЗС-44"
]

class Database:
    def __init__(self):
        self._pool = None
        self._db_url = os.getenv("PG_LINK")

        logger.info("Создан экземпляр Database с URL:s %", self._db_url)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Подключаемся к базе данных и создаем пул соединений"""
        try:
            self._pool = await asyncpg.create_pool(dsn=self._db_url)
            logger.info("Подключение к базе данных установлено")
            await self.create_table()
        except Exception as e:
            logger.error("Ошибка подключения к базе данных: %s", e)
            print("Ошибка подключения к базе данных: %s", e)
            raise

    async def disconnect(self):
        """Закрываем соединение с базой данных"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Соединение с базой данных закрыто")

    async def execute(self, query: str, *args):
        """Выполняем запрос без возврата данных (например, INSERT, UPDATE)"""
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.execute(query, *args)
        return result

    async def fetch(self, query: str, *args):
        """Выполняем запрос с возвратом данных (например, SELECT)"""
        async with self._pool.acquire() as connection:
            result = await connection.fetch(query, *args)
        return result

    async def fetchrow(self, query: str, *args):
        """Выполняем запрос, возвращающий одну строку"""
        async with self._pool.acquire() as connection:
            result = await connection.fetchrow(query, *args)
        return result

    async def fetchval(self, query: str, *args):
        """Выполняем запрос, возвращающий одно значение"""
        async with self._pool.acquire() as connection:
            result = await connection.fetchval(query, *args)
        return result

    async def create_table(self):
        """Создаёт таблицу user_contacts, если её нет, и добавляет столбец company_id_by_contact, если он отсутствует."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS aaskUsers (
        chat_id BIGINT PRIMARY KEY,
        group_name VARCHAR(10) NOT NULL,
        username VARCHAR(50),
        date_registr TIMESTAMP
         );
        """
        await self.execute(create_table_query)
        logger.info("Таблица aaskUsers создана или уже существует.")

    async def add_contact(self, chat_id: int, group_name: str, username: str, date_registr: datetime):
        """Добавляет контакт в таблицу user_contacts с учетом company_id_by_contact"""
        insert_query = """
        INSERT INTO aaskUsers (chat_id, group_name, username, date_registr)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (chat_id) DO UPDATE SET group_name = $2;
        """
        await self.execute(insert_query, chat_id, group_name, username, date_registr)
        logger.info(f"Контакт с chat_id={chat_id}, из группы={group_name}, c именем={username}, в {date_registr} добавлен в базу данных.")
        print(f"Новый пользователь: с chat_id={chat_id}, из группы={group_name}, c именем={username}, в {date_registr} добавлен в базу данных.")

    async def get_group_name_by_chat_id(self, chat_id: int):
        query = """
           SELECT get_group_name
           FROM aaskUsers
           WHERE chat_id = $1;
           """
        company_id = await self.fetchval(query, chat_id)
        if company_id is not None:
            logger.info(f"Найден company_id={company_id} для chat_id={chat_id}.")
            print(f"Найден company_id={company_id} для chat_id={chat_id}.")
        else:
            logger.info(f"Компания для chat_id={chat_id} не найдена.")
            print(f"Компания для chat_id={chat_id} не найдена.")
        return company_id

    async def get_all_group_ids(self):
        """Возвращает все chat_id для каждой группы из базы данных."""
        query = """
        SELECT chat_id, group_name
        FROM aaskUsers
        WHERE group_name = ANY($1);
        """

        result = await self.fetch(query, GROUP_NAMES)
        return result