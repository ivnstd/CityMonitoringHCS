from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных окружения
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    # Создание объекта движка SQLAlchemy
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Проверка соединения с базой данных
    with engine.connect():
        print("Database connection successful")
except OperationalError as e:
    print("Error connecting to database:", e)
