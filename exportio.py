from __future__ import annotations

import json
from typing import Any, Dict, List

from booking import Booking
from logica import Movie
from payments import Payment
from theater import Theater


class Exporter:
    """Экспорт всех данных кинотеатра."""

    @staticmethod
    def to_json(filename: str = "cinema_data.json") -> Dict[str, List[Dict[str, Any]]]:
        """Выгрузить фильмы, сеансы, брони и платежи в JSON."""
        movie = Movie()
        theater = Theater()
        booking = Booking()
        payment = Payment()

        movies = movie.get_all()
        theaters = theater.get_all()
        bookings = booking.get_all()
        payments = payment.get_all()

        data: Dict[str, List[Dict[str, Any]]] = {
            "movies": [movie.to_dict(m) for m in movies],
            "theaters": [theater.to_dict(t) for t in theaters],
            "bookings": [booking.to_dict(b) for b in bookings],
            "payments": [payment.to_dict(p) for p in payments],
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        return data
