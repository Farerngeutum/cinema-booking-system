from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from base_repository import BaseRepository
from db_init import get_db
from exceptions import BookingError
from logica import Seat
from theater import Theater


class Booking(BaseRepository):
    """Класс для работы с бронированиями."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED = "expired"

    @property
    def table_name(self) -> str:
        return "bookings"

    @property
    def field_mapping(self) -> Dict[int, str]:
        return {
            0: "id",
            1: "theater_id",
            2: "guest_name",
            3: "guest_email",
            4: "status",
            5: "total_price",
            6: "created_at",
            7: "confirmed_at",
        }

    @staticmethod
    def create(
        theater_id: int,
        guest_name: str,
        seat_positions: List[Tuple[int, int]],
        guest_email: str = "",
    ) -> int:
        """
        Создать бронирование, занять места и вернуть ID брони.

        Бросает:
            BookingError: если сеанс не найден или места уже заняты.
        """
        theater = Theater()
        theater_data = theater.get(theater_id)
        if theater_data is None:
            raise BookingError("Сеанс не найден.")

        price = theater_data[4]

        if not Seat.check_available(theater_id, seat_positions):
            raise BookingError("Некоторые выбранные места недоступны.")

        total_price = len(seat_positions) * price
        query = """
            INSERT INTO bookings (theater_id, guest_name, guest_email,
                                  total_price, status)
            VALUES (?, ?, ?, ?, ?)
        """
        booking_id = Booking.execute_query(
            query,
            (
                theater_id,
                guest_name,
                guest_email,
                total_price,
                Booking.STATUS_PENDING,
            ),
        )

        Seat.reserve(theater_id, seat_positions, booking_id)
        return booking_id

    @staticmethod
    def get_by_guest(guest_name: str) -> List[Tuple[Any, ...]]:
        """Получить все бронирования по имени гостя."""
        query = "SELECT * FROM bookings WHERE guest_name = ?"
        result = Booking.execute_query(query, (guest_name,), fetch_all=True)
        return result if result else []

    @staticmethod
    def confirm(booking_id: int) -> None:
        """
        Подтвердить бронирование и пометить места как проданные.

        Бросает:
            BookingError: если бронь не найдена или статус не pending.
        """
        booking = Booking()
        booking_data = booking.get(booking_id)
        if booking_data is None:
            raise BookingError("Бронирование не найдено.")

        status = booking_data[4]
        if status != Booking.STATUS_PENDING:
            raise BookingError(f"Бронирование уже в статусе '{status}'.")

        query = """
            UPDATE bookings
            SET status = ?, confirmed_at = ?
            WHERE id = ?
        """
        Booking.execute_query(
            query,
            (Booking.STATUS_CONFIRMED, datetime.now().isoformat(), booking_id),
        )

        Seat.sell(booking_id)

    @staticmethod
    def cancel(booking_id: int) -> None:
        """
        Отменить бронирование и освободить места.

        Бросает:
            BookingError: если бронь не найдена или уже отменена.
        """
        booking = Booking()
        booking_data = booking.get(booking_id)
        if booking_data is None:
            raise BookingError("Бронирование не найдено.")

        status = booking_data[4]
        if status == Booking.STATUS_CANCELLED:
            raise BookingError("Бронирование уже отменено.")

        query = "UPDATE bookings SET status = ? WHERE id = ?"
        Booking.execute_query(query, (Booking.STATUS_CANCELLED, booking_id))

        Seat.free(booking_id)

    @staticmethod
    def mark_expired(booking_id: int) -> None:
        """
        Отметить бронирование как истекшее и освободить места.

        Бросает:
            BookingError: если бронь не найдена.
        """
        booking = Booking()
        booking_data = booking.get(booking_id)
        if booking_data is None:
            raise BookingError("Бронирование не найдено.")

        query = "UPDATE bookings SET status = ? WHERE id = ?"
        Booking.execute_query(query, (Booking.STATUS_EXPIRED, booking_id))

        Seat.free(booking_id)

    @staticmethod
    def to_dict(booking: Optional[Tuple[Any, ...]]) -> Optional[Dict[str, Any]]:
        """Преобразовать бронирование в словарь."""
        if booking is None:
            return None
        seats = Seat.get_by_booking(booking[0])
        return {
            "id": booking[0],
            "theater_id": booking[1],
            "guest_name": booking[2],
            "guest_email": booking[3],
            "status": booking[4],
            "total_price": booking[5],
            "created_at": booking[6],
            "confirmed_at": booking[7],
            "seats_count": len(seats),
        }
