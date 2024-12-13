import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"

def get_db():
    """
    Создает подключение к базе данных и возвращает курсор.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        raise Exception(f"Ошибка подключения к базе данных: {e}")

def close_db(conn, cursor):
    """
    Закрывает подключение к базе данных.
    """
    if cursor:
        cursor.close()
    if conn:
        conn.close()