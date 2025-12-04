from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from base_repository import BaseRepository
from db_init import get_db


class Movie(BaseRepository):
    """Класс для работы с фильмами."""

    @property
    def table_name(self) -> str:
        return "movies"

    @property
    def field_mapping(self) -> Dict[int, str]:
        return {
            0: "id",
            1: "title",
            2: "duration",
            3: "rating",
            4: "description",
        }

    @staticmethod
    def add(
        title: str,
        duration: int,
        rating: float = 0.0,
        description: str = "",
    ) -> Optional[int]:
        """Добавить фильм и вернуть его ID или None, если уже есть."""
        query = """
            INSERT INTO movies (title, duration, rating, description)
            VALUES (?, ?, ?, ?)
        """
        try:
            return Movie.execute_query(query, (title, duration, rating, description))
        except sqlite3.IntegrityError:
            return None

    @staticmethod
    def update(
        movie_id: int,
        **kwargs: Any,
    ) -> None:
        """Обновить данные фильма по ID."""
        if not kwargs:
            return

        allowed_fields = {"title", "duration", "rating", "description"}
        fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields_to_update:
            return

        set_clause = ", ".join([f"{key} = ?" for key in fields_to_update.keys()])
        query = f"UPDATE movies SET {set_clause} WHERE id = ?"
        params = tuple(fields_to_update.values()) + (movie_id,)

        Movie.execute_query(query, params)


class Seat(BaseRepository):
    """Класс для работы с местами в зале."""

    STATUS_FREE = "free"
    STATUS_RESERVED = "reserved"
    STATUS_SOLD = "sold"

    @property
    def table_name(self) -> str:
        return "seats"

    @property
    def field_mapping(self) -> Dict[int, str]:
        return {
            0: "id",
            1: "theater_id",
            2: "row",
            3: "col",
            4: "status",
            5: "booking_id",
        }

    @staticmethod
    def get_available(theater_id: int) -> List[Tuple[Any, ...]]:
        """Получить список свободных мест для сеанса."""
        query = """
            SELECT * FROM seats
            WHERE theater_id = ? AND status = ?
        """
        result = Seat.execute_query(query, (theater_id, Seat.STATUS_FREE), fetch_all=True)
        return result if result else []

    @staticmethod
    def get_by_position(
        theater_id: int,
        row: int,
        col: int,
    ) -> Optional[Tuple[Any, ...]]:
        """Получить одно место по ряду и месту."""
        query = """
            SELECT * FROM seats
            WHERE theater_id = ? AND row = ? AND col = ?
        """
        return Seat.execute_query(query, (theater_id, row, col), fetch_one=True)

    @staticmethod
    def get_by_booking(booking_id: int) -> List[Tuple[int, int]]:
        """Получить список (ряд, место) по ID бронирования."""
        query = "SELECT row, col FROM seats WHERE booking_id = ?"
        result = Seat.execute_query(query, (booking_id,), fetch_all=True)
        return result if result else []

    @staticmethod
    def check_available(
        theater_id: int,
        seat_positions: list[tuple[int, int]],
    ) -> bool:
        """Проверить, что все указанные места свободны."""
        for row, col in seat_positions:
            query = """
                SELECT 1 FROM seats
                WHERE theater_id = ?
                  AND row = ?
                  AND col = ?
                  AND status = ?
            """
            result = Seat.execute_query(
                query,
                (theater_id, row, col, Seat.STATUS_FREE),
                fetch_one=True,
            )
            if result is None:
                return False
        return True

    @staticmethod
    def reserve(
        theater_id: int,
        seat_positions: list[tuple[int, int]],
        booking_id: int,
    ) -> None:
        """Пометить места как забронированные и привязать к брони."""
        query = """
            UPDATE seats
            SET status = ?, booking_id = ?
            WHERE theater_id = ? AND row = ? AND col = ?
        """
        for row, col in seat_positions:
            Seat.execute_query(query, (Seat.STATUS_RESERVED, booking_id, theater_id, row, col))

    @staticmethod
    def sell(booking_id: int) -> None:
        """Пометить места брони как проданные."""
        query = """
            UPDATE seats
            SET status = ?
            WHERE booking_id = ?
        """
        Seat.execute_query(query, (Seat.STATUS_SOLD, booking_id))

    @staticmethod
    def free(booking_id: int) -> None:
        """Освободить места для указанной брони."""
        query = """
            UPDATE seats
            SET status = ?, booking_id = NULL
            WHERE booking_id = ?
        """
        Seat.execute_query(query, (Seat.STATUS_FREE, booking_id))
