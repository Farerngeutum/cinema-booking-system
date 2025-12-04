"""Тесты для класса Payment."""

import unittest
from db_init import clear_db, init_db
from logica import Movie
from theater import Theater
from booking import Booking
from payments import Payment
from exceptions import PaymentError


class TestPayment(unittest.TestCase):
    """Тесты операций с платежами."""

    def setUp(self):
        """Инициализировать БД и создать тестовое бронирование."""
        clear_db()
        init_db()
        movie_id = Movie.add("Тестовый фильм", 120, 8.0, "Описание")
        self.theater_id = Theater.add(movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        self.booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(1, 1), (1, 2)],
        )

    def test_process_payment_success(self):
        """Тест успешной обработки платежа."""
        booking = Booking().get(self.booking_id)
        payment_id = Payment.process(self.booking_id, booking[5])
        self.assertIsNotNone(payment_id)
        self.assertIsInstance(payment_id, int)

    def test_process_payment_nonexistent_booking(self):
        """Тест платежа для несуществующего бронирования."""
        with self.assertRaises(PaymentError):
            Payment.process(9999, 500.0)

    def test_process_payment_wrong_amount(self):
        """Тест платежа с неправильной суммой."""
        booking = Booking().get(self.booking_id)
        correct_amount = booking[5]
        with self.assertRaises(PaymentError):
            Payment.process(self.booking_id, correct_amount + 100)

    def test_process_payment_creates_transaction_id(self):
        """Тест что платёж создаёт уникальный transaction_id."""
        booking = Booking().get(self.booking_id)
        payment_id = Payment.process(self.booking_id, booking[5])
        payment = Payment().get(payment_id)
        self.assertIsNotNone(payment[4])  # transaction_id
        self.assertGreater(len(payment[4]), 0)

    def test_get_payment_by_booking(self):
        """Тест получения платежа по ID бронирования."""
        booking = Booking().get(self.booking_id)
        Payment.process(self.booking_id, booking[5])
        payment = Payment.get_by_booking(self.booking_id)
        self.assertIsNotNone(payment)
        self.assertEqual(payment[1], self.booking_id)

    def test_get_all_payments(self):
        """Тест получения всех платежей."""
        booking = Booking().get(self.booking_id)
        Payment.process(self.booking_id, booking[5])
        payments = Payment().get_all()
        self.assertGreater(len(payments), 0)

    def test_payment_status_completed(self):
        """Тест что статус платежа всегда completed."""
        booking = Booking().get(self.booking_id)
        payment_id = Payment.process(self.booking_id, booking[5])
        payment = Payment().get(payment_id)
        self.assertEqual(payment[3], Payment.STATUS_COMPLETED)

    def test_to_dict(self):
        """Тест преобразования платежа в словарь."""
        booking = Booking().get(self.booking_id)
        payment_id = Payment.process(self.booking_id, booking[5])
        payment = Payment().get(payment_id)
        payment_dict = Payment().to_dict(payment)
        self.assertIsNotNone(payment_dict)
        self.assertEqual(payment_dict["booking_id"], self.booking_id)
        self.assertEqual(payment_dict["status"], Payment.STATUS_COMPLETED)


if __name__ == "__main__":
    unittest.main()
