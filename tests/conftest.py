"""Общие фиксчуры и утилиты для тестов."""

import os
from db_init import clear_db, init_db


def setup_test_db():
    """Подготовить БД для тестов."""
    clear_db()
    init_db()


def teardown_test_db():
    """Очистить БД после тестов."""
    if os.path.exists("cinema.db"):
        os.remove("cinema.db")
