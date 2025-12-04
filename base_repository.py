from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from db_init import get_db


class BaseRepository(ABC):
    """
    Абстрактный базовый класс для работы с БД.

    Содержит общие CRUD операции для всех сущностей.
    Дочерние классы должны переопределить:
        - table_name: название таблицы
        - field_mapping: маппинг полей из БД в словарь
    """

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Название таблицы в БД."""
        pass

    @property
    @abstractmethod
    def field_mapping(self) -> Dict[int, str]:
        """Маппинг индексов tuple на названия полей в словаре."""
        pass

    @staticmethod
    def execute_query(
            query: str,
            params: tuple = (),
            fetch_one: bool = False,
            fetch_all: bool = False,
    ) -> Optional[Any]:
        """
        Выполнить SQL запрос и вернуть результат.

        Args:
            query: SQL запрос
            params: параметры для запроса
            fetch_one: вернуть одну строку
            fetch_all: вернуть все строки

        Returns:
            Результат запроса или None
        """
        with get_db() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            return cursor.lastrowid

    def get(self, entity_id: int) -> Optional[Tuple[Any, ...]]:
        """Получить одну сущность по ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.execute_query(query, (entity_id,), fetch_one=True)

    def get_all(self) -> List[Tuple[Any, ...]]:
        """Получить все сущности."""
        query = f"SELECT * FROM {self.table_name}"
        result = self.execute_query(query, fetch_all=True)
        return result if result else []

    def delete(self, entity_id: int) -> None:
        """Удалить сущность по ID."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self.execute_query(query, (entity_id,))

    def to_dict(
            self,
            entity: Optional[Tuple[Any, ...]],
    ) -> Optional[Dict[str, Any]]:
        """Преобразовать tuple в словарь по маппингу."""
        if entity is None:
            return None
        return {key: entity[idx] for idx, key in self.field_mapping.items()}
