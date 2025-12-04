from __future__ import annotations

from datetime import datetime, timedelta

from booking import Booking
from db_init import clear_db, init_db
from exceptions import BookingError, PaymentError
from exportio import Exporter
from logica import Movie
from payments import Payment
from seed_data import seed_movies, seed_theaters
from theater import Theater


def main() -> None:
    """Пример работы системы бронирования кино."""
    clear_db()
    init_db()

    # Ручной фильм и сеанс
    avatar_id = Movie.add("Аватар 3", 192, 8.5, "Эпический фильм")
    schedule = (datetime.now() + timedelta(days=1, hours=18)).isoformat()
    theater_id = Theater.add(avatar_id, 5, 8, 250.0, schedule)

    # Автозаполнение с Faker
    movie_ids = seed_movies(3)
    theater_ids = seed_theaters(movie_ids, per_movie=2)

    print("Созданы фильмы:", [avatar_id, *movie_ids])
    print("Созданы сеансы:", [theater_id, *theater_ids])

    # Показать схему мест
    Theater.show_seat_map(theater_id)

    try:
        # Создание бронирования
        booking_id = Booking.create(
            theater_id=theater_id,
            guest_name="Иван Петров",
            seat_positions=[(1, 1), (1, 2), (1, 3)],
            guest_email="ivan@example.com",
        )
        print(f"Бронирование создано, ID: {booking_id}")

        Theater.show_seat_map(theater_id)

        # Оплата
        booking = Booking()
        booking_data = booking.get(booking_id)
        if booking_data is None:
            raise BookingError("Бронирование исчезло перед оплатой.")

        total_price = booking_data[5]
        payment_id = Payment.process(booking_id, total_price)
        print(f"Платёж выполнен, ID: {payment_id}")

        # Подтверждение
        Booking.confirm(booking_id)
        print("Бронирование подтверждено.")

        Theater.show_seat_map(theater_id)

    except (BookingError, PaymentError) as error:
        print(f"Ошибка: {error}")

    # Вывод всех данных
    print("\nВсе фильмы:")
    movie = Movie()
    for m in movie.get_all():
        m_dict = movie.to_dict(m)
        print(f"  {m_dict['title']} - {m_dict['duration']} мин")

    print("\nВсе сеансы:")
    theater = Theater()
    for t in theater.get_all():
        t_dict = theater.to_dict(t)
        print(f"  ID: {t_dict['id']}, Цена: {t_dict['price']}₽")

    print("\nВсе бронирования:")
    booking = Booking()
    for b in booking.get_all():
        b_dict = booking.to_dict(b)
        print(f"  {b_dict['guest_name']} - {b_dict['status']} ({b_dict['total_price']}₽)")

    print("\nВсе платежи:")
    payment = Payment()
    for p in payment.get_all():
        p_dict = payment.to_dict(p)
        print(f"  {p_dict['amount']}₽ - {p_dict['status']}")

    # Экспорт
    Exporter.to_json()
    print("\nДанные экспортированы в cinema_data.json")


if __name__ == "__main__":
    main()
