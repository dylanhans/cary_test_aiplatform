# app/models/database.py
import psycopg2
from contextlib import contextmanager
from app.core.config import settings

@contextmanager
def get_db():
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()