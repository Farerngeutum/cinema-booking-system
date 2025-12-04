"""Тесты для класса Booking."""

import unittest
from db_init import clear_db, init_db
from logica import Movie, Seat
from theater import Theater
from booking import Booking
from exceptions import BookingError


class TestBooking(unittest.TestCase):
    """Тесты операций с бронированиями."""

    def setUp(self):
        """Инициализировать БД и создать тестовый сеанс."""
        clear_db()
        init_db()
        movie_id = Movie.add("Тестовый фильм", 120, 8.0, "Описание")
        self.theater_id = Theater.add(movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")

    def test_create_booking_success(self):
        """Тест успешного создания бронирования."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван Петров",
            seat_positions=[(1, 1), (1, 2)],
            guest_email="ivan@example.com",
        )
        self.assertIsNotNone(booking_id)
        self.assertIsInstance(booking_id, int)

    def test_create_booking_nonexistent_theater(self):
        """Тест создания бронирования для несуществующего сеанса."""
        with self.assertRaises(BookingError):
            Booking.create(
                theater_id=9999,
                guest_name="Иван",
                seat_positions=[(1, 1)],
            )

    def test_create_booking_unavailable_seat(self):
        """Тест попытки забронировать уже занятое место."""
        Booking.create(
            theater_id=self.theater_id,
            guest_name="Гость 1",
            seat_positions=[(1, 1)],
        )
        with self.assertRaises(BookingError):
            Booking.create(
                theater_id=self.theater_id,
                guest_name="Гость 2",
                seat_positions=[(1, 1)],
            )

    def test_create_booking_reserves_seats(self):
        """Тест что при создании бронирования места помечаются как зарезервированные."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(2, 2), (2, 3)],
        )
        seat = Seat.get_by_position(self.theater_id, 2, 2)
        self.assertEqual(seat[4], Seat.STATUS_RESERVED)
        self.assertEqual(seat[5], booking_id)

    def test_confirm_booking_success(self):
        """Тест успешного подтверждения бронирования."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(1, 1)],
        )
        Booking.confirm(booking_id)
        booking = Booking().get(booking_id)
        self.assertEqual(booking[4], Booking.STATUS_CONFIRMED)

    def test_confirm_booking_seats_become_sold(self):
        """Тест что при подтверждении места становятся проданными."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(1, 1)],
        )
        Booking.confirm(booking_id)
        seat = Seat.get_by_position(self.theater_id, 1, 1)
        self.assertEqual(seat[4], Seat.STATUS_SOLD)

    def test_confirm_nonexistent_booking(self):
        """Тест подтверждения несуществующего бронирования."""
        with self.assertRaises(BookingError):
            Booking.confirm(9999)

    def test_confirm_already_confirmed_booking(self):
        """Тест попытки подтвердить уже подтвёрённое бронирование."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(1, 1)],
        )
        Booking.confirm(booking_id)
        with self.assertRaises(BookingError):
            Booking.confirm(booking_id)

    def test_cancel_booking_success(self):
        """Тест успешной отмены бронирования."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(3, 3)],
        )
        Booking.cancel(booking_id)
        booking = Booking().get(booking_id)
        self.assertEqual(booking[4], Booking.STATUS_CANCELLED)

    def test_cancel_booking_frees_seats(self):
        """Тест что при отмене места освобождаются."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(3, 3)],
        )
        Booking.cancel(booking_id)
        seat = Seat.get_by_position(self.theater_id, 3, 3)
        self.assertEqual(seat[4], Seat.STATUS_FREE)
        self.assertIsNone(seat[5])

    def test_get_booking_by_guest(self):
        """Тест получения бронирований по имени гостя."""
        Booking.create(
            theater_id=self.theater_id,
            guest_name="Александр",
            seat_positions=[(1, 1)],
        )
        Booking.create(
            theater_id=self.theater_id,
            guest_name="Александр",
            seat_positions=[(2, 2)],
        )
        bookings = Booking.get_by_guest("Александр")
        self.assertEqual(len(bookings), 2)

    def test_to_dict(self):
        """Тест преобразования бронирования в словарь."""
        booking_id = Booking.create(
            theater_id=self.theater_id,
            guest_name="Иван",
            seat_positions=[(1, 1), (1, 2)],
            guest_email="ivan@example.com",
        )
        booking = Booking().get(booking_id)
        booking_dict = Booking().to_dict(booking)
        self.assertIsNotNone(booking_dict)
        self.assertEqual(booking_dict["guest_name"], "Иван")
        self.assertEqual(booking_dict["seats_count"], 2)


if __name__ == "__main__":
    unittest.main()
