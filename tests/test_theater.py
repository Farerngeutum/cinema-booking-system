"""Тесты для класса Theater."""

import unittest
from db_init import clear_db, init_db
from logica import Movie, Seat
from theater import Theater


class TestTheater(unittest.TestCase):
    """Тесты операций с залами/сеансами."""

    def setUp(self):
        """Инициализировать БД и создать тестовый фильм."""
        clear_db()
        init_db()
        self.movie_id = Movie.add("Тестовый фильм", 120, 8.0, "Описание")

    def test_add_theater_success(self):
        """Тест успешного создания сеанса."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        self.assertIsNotNone(theater_id)
        self.assertIsInstance(theater_id, int)

    def test_add_theater_creates_seats(self):
        """Тест что при создании сеанса создаются все места."""
        theater_id = Theater.add(self.movie_id, 3, 4, 300.0, "2025-01-01T18:00:00")
        seats = Seat().get_all()
        self.assertEqual(len(seats), 12)  # 3x4 = 12 мест

    def test_add_theater_nonexistent_movie(self):
        """Тест создания сеанса для несуществующего фильма."""
        result = Theater.add(9999, 5, 8, 250.0, "2025-01-01T18:00:00")
        self.assertIsNone(result)

    def test_get_theater_by_id(self):
        """Тест получения сеанса по ID."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        theater = Theater().get(theater_id)
        self.assertIsNotNone(theater)
        self.assertEqual(theater[1], self.movie_id)
        self.assertEqual(theater[4], 250.0)

    def test_get_all_theaters(self):
        """Тест получения всех сеансов."""
        Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        Theater.add(self.movie_id, 4, 6, 300.0, "2025-01-01T20:00:00")
        theaters = Theater().get_all()
        self.assertEqual(len(theaters), 2)

    def test_update_theater_price(self):
        """Тест обновления цены сеанса."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        Theater.update(theater_id, price=350.0)
        updated = Theater().get(theater_id)
        self.assertEqual(updated[4], 350.0)

    def test_update_theater_schedule(self):
        """Тест обновления времени сеанса."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        new_schedule = "2025-01-02T20:00:00"
        Theater.update(theater_id, schedule=new_schedule)
        updated = Theater().get(theater_id)
        self.assertEqual(updated[5], new_schedule)

    def test_delete_theater(self):
        """Тест удаления сеанса."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        Theater().delete(theater_id)
        deleted = Theater().get(theater_id)
        self.assertIsNone(deleted)

    def test_to_dict(self):
        """Тест преобразования сеанса в словарь."""
        theater_id = Theater.add(self.movie_id, 5, 8, 250.0, "2025-01-01T18:00:00")
        theater = Theater().get(theater_id)
        theater_dict = Theater().to_dict(theater)
        self.assertIsNotNone(theater_dict)
        self.assertEqual(theater_dict["price"], 250.0)
        self.assertEqual(theater_dict["rows"], 5)


if __name__ == "__main__":
    unittest.main()
