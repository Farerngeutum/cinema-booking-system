import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

DB_NAME = "cinema.db"


def get_connection() -> sqlite3.Connection:
    """Создать и вернуть соединение с БД."""
    return sqlite3.connect(DB_NAME)


@contextmanager
def get_db() -> Generator[sqlite3.Cursor, None, None]:
    """
    Контекстный менеджер для работы с БД.

    Использование:
        with get_db() as cursor:
            cursor.execute("SELECT * FROM movies")
    """
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Создать БД и таблицы, если их ещё нет."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            duration INTEGER NOT NULL,
            rating REAL DEFAULT 0.0,
            description TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS theaters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            rows INTEGER NOT NULL,
            cols INTEGER NOT NULL,
            price REAL NOT NULL,
            schedule TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theater_id INTEGER NOT NULL,
            row INTEGER NOT NULL,
            col INTEGER NOT NULL,
            status TEXT DEFAULT 'free',
            booking_id INTEGER,
            FOREIGN KEY (theater_id) REFERENCES theaters(id),
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theater_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            guest_email TEXT,
            status TEXT DEFAULT 'pending',
            total_price REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TEXT,
            FOREIGN KEY (theater_id) REFERENCES theaters(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER UNIQUE NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'completed',
            transaction_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
        """
    )

    conn.commit()
    conn.close()


def clear_db() -> None:
    """Удалить БД и создать пустую заново."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
