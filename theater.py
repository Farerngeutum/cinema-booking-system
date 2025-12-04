from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from base_repository import BaseRepository
from db_init import get_db
from logica import Movie, Seat


class Theater(BaseRepository):
    """Класс для работы с залами и сеансами."""

    @property
    def table_name(self) -> str:
        return "theaters"

    @property
    def field_mapping(self) -> Dict[int, str]:
        return {
            0: "id",
            1: "movie_id",
            2: "rows",
            3: "cols",
            4: "price",
            5: "schedule",
        }

    @staticmethod
    def add(
        movie_id: int,
        rows: int,
        cols: int,
        price: float,
        schedule: str,
    ) -> Optional[int]:
        """Создать сеанс и места для него."""
        movie = Movie()
        if movie.get(movie_id) is None:
            return None

        query = """
            INSERT INTO theaters (movie_id, rows, cols, price, schedule)
            VALUES (?, ?, ?, ?, ?)
        """

        with get_db() as cursor:
            theater_id = cursor.execute(query, (movie_id, rows, cols, price, schedule)).lastrowid

            for row in range(1, rows + 1):
                for col in range(1, cols + 1):
                    cursor.execute(
                        """
                        INSERT INTO seats (theater_id, row, col, status)
                        VALUES (?, ?, ?, ?)
                        """,
                        (theater_id, row, col, Seat.STATUS_FREE),
                    )

        return theater_id

    @staticmethod
    def update(
        theater_id: int,
        **kwargs: Any,
    ) -> None:
        """Обновить сеанс по ID."""
        if not kwargs:
            return

        allowed_fields = {"price", "schedule"}
        fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields_to_update:
            return

        set_clause = ", ".join([f"{key} = ?" for key in fields_to_update.keys()])
        query = f"UPDATE theaters SET {set_clause} WHERE id = ?"
        params = tuple(fields_to_update.values()) + (theater_id,)

        Theater.execute_query(query, params)

    @staticmethod
    def show_seat_map(theater_id: int) -> None:
        """Показать схему мест для сеанса."""
        theater = Theater()
        theater_data = theater.get(theater_id)
        if theater_data is None:
            print("Сеанс не найден.")
            return

        rows, cols = theater_data[2], theater_data[3]
        seats = Seat()
        seat_list = seats.get_all()

        seat_status: dict[tuple[int, int], str] = {}
        for seat_row in seat_list:
            if seat_row[1] == theater_id:
                seat_status[(seat_row[2], seat_row[3])] = seat_row[4]

        print(f"\nСхема мест (всего {rows}x{cols}):\n")
        print("   ", end="")
        for col in range(1, cols + 1):
            print(f"{col:3}", end="")
        print()

        for row in range(1, rows + 1):
            print(f"{row:2} ", end="")
            for col in range(1, cols + 1):
                status = seat_status.get((row, col), Seat.STATUS_FREE)
                if status == Seat.STATUS_FREE:
                    print(" ⭕", end="")
                elif status == Seat.STATUS_RESERVED:
                    print(" 🟡", end="")
                elif status == Seat.STATUS_SOLD:
                    print(" 🔴", end="")
            print()

        print("\n⭕ = Свободно | 🟡 = Зарезервировано | 🔴 = Продано\n")
