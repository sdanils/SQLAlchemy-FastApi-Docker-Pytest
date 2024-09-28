from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Engine
import configparser

def get_engine_db() -> Engine:
    """
    Функция для создания соеденения с БД
    
    :return: Engine соединение
    """
    #Чтение данных для  URL БД
    config = configparser.ConfigParser()
    config.read('config.ini')

    user = config['database']['user']
    password = config['database']['password']
    host = config['database']['host']
    dbname = config['database']['dbname']

    #Формирование строки БД
    DATABASE_URL = f"postgresql://{user}:{password}@{host}/{dbname}"

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

