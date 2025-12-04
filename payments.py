from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from base_repository import BaseRepository
from booking import Booking
from exceptions import PaymentError


class Payment(BaseRepository):
    """Класс для работы с платежами."""

    STATUS_COMPLETED = "completed"

    @property
    def table_name(self) -> str:
        return "payments"

    @property
    def field_mapping(self) -> Dict[int, str]:
        return {
            0: "id",
            1: "booking_id",
            2: "amount",
            3: "status",
            4: "transaction_id",
            5: "created_at",
        }

    @staticmethod
    def process(booking_id: int, amount: float) -> int:
        """
        Обработать платёж и вернуть ID платежа.

        Бросает:
            PaymentError: если бронь не найдена или сумма не совпадает.
        """
        booking = Booking()
        booking_data = booking.get(booking_id)
        if booking_data is None:
            raise PaymentError("Бронирование не найдено.")

        expected_amount = booking_data[5]
        if amount != expected_amount:
            raise PaymentError(
                f"Сумма не совпадает: ожидалось {expected_amount}, "
                f"получено {amount}."
            )

        transaction_id = str(uuid.uuid4())
        query = """
            INSERT INTO payments (booking_id, amount, status, transaction_id)
            VALUES (?, ?, ?, ?)
        """
        return Payment.execute_query(
            query,
            (
                booking_id,
                amount,
                Payment.STATUS_COMPLETED,
                transaction_id,
            ),
        )

    @staticmethod
    def get_by_booking(booking_id: int) -> Optional[Tuple[Any, ...]]:
        """Получить платёж по ID бронирования."""
        query = "SELECT * FROM payments WHERE booking_id = ?"
        return Payment.execute_query(query, (booking_id,), fetch_one=True)

    @staticmethod
    def to_dict(payment: Optional[Tuple[Any, ...]]) -> Optional[Dict[str, Any]]:
        """Преобразовать платёж в словарь."""
        if payment is None:
            return None
        return {
            "id": payment[0],
            "booking_id": payment[1],
            "amount": payment[2],
            "status": payment[3],
            "transaction_id": payment[4],
            "created_at": payment[5],
        }
