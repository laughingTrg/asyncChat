from pathlib import Path
import os

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# env
DOTENV_PATH = BASE_DIR / '.env'

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
""" Получение значения параметров из файла .env """


class Config():
    """
        Основные настройки базы данных
            DEBUG - Подключение режима отладки и вывода информации о всех запросах
            SECRET_KEY - Ключ для подключения к базе данных
            SQLALCHEMY_DATABASE_URI - место размещения базы данных
    """
    DEBUG = os.getenv('DEBUG')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(BASE_DIR, 'server_config/db', 'messenger.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
    DATABASE_CONNECT_OPTIONS = {}
