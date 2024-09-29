from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Engine
from pydantic_settings import BaseSettings

#Класс для хранения настроек БД
class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str 

    class Config:
        env_file = ".env"

settings = Settings()

def get_engine_db() -> Engine:
    """
    Функция для создания соеденения с БД
    :return: Engine соединение
    """
    #Формирование строки БД в контейнере!!!
    DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@db/{settings.postgres_db}"
    
    #Формирование строки БД для тестов на основной машине, если БД настроен на такие параметры
    #DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}"
    
    #Создание объекта Engine
    engine = create_engine(DATABASE_URL)
    return engine


def get_session_maker() -> sessionmaker:
    """
    Функция для создания фабрики сессий
    :return: фабрика сессий
    """
    #Получение соединения с бд
    engine = get_engine_db()
    # Создание фабрики для сессий
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return SessionLocal

