from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from faker import Faker

from logica import Movie
from theater import Theater

fake = Faker("ru_RU")


def seed_movies(count: int = 5) -> List[int]:
    """Создать случайные фильмы и вернуть их ID."""
    movie_ids: List[int] = []

    for _ in range(count):
        title = fake.sentence(nb_words=3).rstrip(".")
        duration = fake.random_int(min=80, max=180)
        rating = round(fake.pyfloat(min_value=4.0, max_value=9.5), 1)
        description = fake.text(max_nb_chars=120)

        movie_id = Movie.add(
            title=title,
            duration=duration,
            rating=rating,
            description=description,
        )
        if movie_id is not None:
            movie_ids.append(movie_id)

    return movie_ids


def seed_theaters(movie_ids: List[int], per_movie: int = 2) -> List[int]:
    """Создать случайные сеансы для фильмов и вернуть их ID."""
    theater_ids: List[int] = []

    for movie_id in movie_ids:
        for _ in range(per_movie):
            rows = fake.random_int(min=4, max=8)
            cols = fake.random_int(min=6, max=12)
            price = fake.random_int(min=200, max=600)

            start_time = datetime.now() + timedelta(
                days=fake.random_int(min=0, max=3),
                hours=fake.random_int(min=10, max=23),
            )
            schedule = start_time.isoformat()

            theater_id = Theater.add(
                movie_id=movie_id,
                rows=rows,
                cols=cols,
                price=price,
                schedule=schedule,
            )
            if theater_id is not None:
                theater_ids.append(theater_id)

    return theater_ids
