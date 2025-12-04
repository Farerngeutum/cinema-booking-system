"""Тесты для класса Seat."""

import unittest
from db_init import clear_db, init_db
from logica import Movie, Seat
from theater import Theater


class TestSeat(unittest.TestCase):
    """Тесты операций с местами."""

    def setUp(self):
        """Инициализировать БД и создать тестовый сеанс."""
        clear_db()
        init_db()
        movie_id = Movie.add("Тестовый фильм", 120, 8.0, "Описание")
        self.theater_id = Theater.add(movie_id, 3, 3, 300.0, "2025-01-01T18:00:00")

    def test_get_all_seats(self):
        """Тест получения всех мест сеанса."""
        seats = Seat().get_all()
        self.assertEqual(len(seats), 9)  # 3x3 = 9 мест

    def test_get_available_seats(self):
        """Тест получения свободных мест."""
        available = Seat.get_available(self.theater_id)
        self.assertEqual(len(available), 9)

    def test_get_seat_by_position(self):
        """Тест получения места по координатам."""
        seat = Seat.get_by_position(self.theater_id, 1, 1)
        self.assertIsNotNone(seat)
        self.assertEqual(seat[2], 1)  # row
        self.assertEqual(seat[3], 1)  # col
        self.assertEqual(seat[4], Seat.STATUS_FREE)

    def test_check_available_free_seats(self):
        """Тест проверки доступности свободных мест."""
        result = Seat.check_available(self.theater_id, [(1, 1), (1, 2)])
        self.assertTrue(result)

    def test_check_available_reserved_seat_fails(self):
        """Тест проверки на зарезервированное место."""
        Seat.reserve(self.theater_id, [(1, 1)], booking_id=1)
        result = Seat.check_available(self.theater_id, [(1, 1)])
        self.assertFalse(result)

    def test_reserve_seats(self):
        """Тест резервирования мест."""
        Seat.reserve(self.theater_id, [(1, 1), (1, 2)], booking_id=1)
        seat = Seat.get_by_position(self.theater_id, 1, 1)
        self.assertEqual(seat[4], Seat.STATUS_RESERVED)
        self.assertEqual(seat[5], 1)  # booking_id

    def test_sell_seats(self):
        """Тест продажи мест."""
        Seat.reserve(self.theater_id, [(2, 2)], booking_id=5)
        Seat.sell(5)
        seat = Seat.get_by_position(self.theater_id, 2, 2)
        self.assertEqual(seat[4], Seat.STATUS_SOLD)

    def test_free_seats(self):
        """Тест освобождения мест."""
        Seat.reserve(self.theater_id, [(3, 3)], booking_id=10)
        Seat.free(10)
        seat = Seat.get_by_position(self.theater_id, 3, 3)
        self.assertEqual(seat[4], Seat.STATUS_FREE)
        self.assertIsNone(seat[5])  # booking_id = NULL

    def test_get_by_booking(self):
        """Тест получения мест по ID бронирования."""
        Seat.reserve(self.theater_id, [(1, 1), (1, 2), (1, 3)], booking_id=7)
        seats = Seat.get_by_booking(7)
        self.assertEqual(len(seats), 3)
        self.assertIn((1, 1), seats)


if __name__ == "__main__":
    unittest.main()
