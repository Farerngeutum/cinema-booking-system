"""Тесты для класса Movie."""

import unittest
from db_init import clear_db, init_db
from logica import Movie


class TestMovie(unittest.TestCase):
    """Тесты операций с фильмами."""

    def setUp(self):
        """Инициализировать БД перед каждым тестом."""
        clear_db()
        init_db()

    def test_add_movie_success(self):
        """Тест успешного добавления фильма."""
        movie_id = Movie.add("Тестовый фильм", 120, 8.5, "Описание")
        self.assertIsNotNone(movie_id)
        self.assertIsInstance(movie_id, int)

    def test_add_duplicate_movie_fails(self):
        """Тест добавления фильма с дублирующимся названием."""
        Movie.add("Уникальный фильм", 100, 7.0, "Описание")
        result = Movie.add("Уникальный фильм", 110, 7.5, "Другое описание")
        self.assertIsNone(result)

    def test_get_movie_by_id(self):
        """Тест получения фильма по ID."""
        movie_id = Movie.add("Фильм для поиска", 130, 8.0, "Описание")
        movie = Movie().get(movie_id)
        self.assertIsNotNone(movie)
        self.assertEqual(movie[1], "Фильм для поиска")

    def test_get_nonexistent_movie(self):
        """Тест получения несуществующего фильма."""
        movie = Movie().get(9999)
        self.assertIsNone(movie)

    def test_get_all_movies(self):
        """Тест получения всех фильмов."""
        Movie.add("Фильм 1", 100, 7.0, "Описание 1")
        Movie.add("Фильм 2", 110, 8.0, "Описание 2")
        movies = Movie().get_all()
        self.assertEqual(len(movies), 2)

    def test_update_movie(self):
        """Тест обновления данных фильма."""
        movie_id = Movie.add("Оригинальное название", 100, 7.0, "Описание")
        Movie.update(movie_id, title="Новое название", duration=120)
        updated_movie = Movie().get(movie_id)
        self.assertEqual(updated_movie[1], "Новое название")
        self.assertEqual(updated_movie[2], 120)

    def test_delete_movie(self):
        """Тест удаления фильма."""
        movie_id = Movie.add("Фильм для удаления", 100, 7.0, "Описание")
        Movie().delete(movie_id)
        deleted_movie = Movie().get(movie_id)
        self.assertIsNone(deleted_movie)

    def test_to_dict(self):
        """Тест преобразования фильма в словарь."""
        movie_id = Movie.add("Фильм", 120, 8.5, "Описание")
        movie = Movie().get(movie_id)
        movie_dict = Movie().to_dict(movie)
        self.assertIsNotNone(movie_dict)
        self.assertEqual(movie_dict["title"], "Фильм")
        self.assertEqual(movie_dict["duration"], 120)


if __name__ == "__main__":
    unittest.main()
