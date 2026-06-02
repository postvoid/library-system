from __future__ import annotations
from uuid import uuid4
from exceptions import BookNotAvailableError


class Book:
    """Представляет книгу в библиотечной системе."""

    def __init__(
        self,
        title: str,
        author: str,
        book_id: str | None = None,
        isbn: str | None = None,
        metadata: dict[str, str] | None = None,
        available: bool = True,
    ) -> None:
        """
        Инициализация новой книги.

        Аргументы:
            title: Название книги (обязательно)
            author: Автор книги (обязательно)
            book_id: Уникальный идентификатор (генерируется автоматически если None)
            isbn: ISBN номер (опционально)
            metadata: Дополнительные метаданные словарем (ключи и значения - строки)
            available: Начальный статус доступности

        Исключения:
            ValueError: Если title или author пустые
        """
        if not title:
            raise ValueError("Название книги обязательно!")
        if not author:
            raise ValueError("Автор книги обязателен!")

        self.book_id: str = str(book_id) if book_id is not None else str(uuid4())
        self.title: str = title
        self.author: str = author
        self.isbn: str | None = isbn
        self.metadata: dict[str, str] | None = metadata if metadata is not None else {}
        self._available: bool = available

    def is_available(self) -> bool:
        """Возвращает True, если книга доступна для выдачи."""
        return self._available

    def borrow(self) -> None:
        """
        Отмечает книгу как выданную.

        Исключения:
            BookNotAvailableError: Если книга уже выдана
        """
        if not self._available:
            raise BookNotAvailableError(f"Книга {self.book_id} недоступна")
        self._available = False

    def return_book(self) -> None:
        """
        Отмечает книгу как доступную (возвращённую).

        Исключения:
            BookNotAvailableError: Если книга не была выдана
        """
        if self._available:
            raise BookNotAvailableError("Книга не была выдана")
        self._available = True

    def to_dict(self) -> dict[str, str | bool | dict[str, str] | None]:
        """
        Преобразует книгу в словарь для сериализации.

        Возвращает:
            Словарь с полями: id, title, author, isbn, available, metadata
        """
        # Приводим metadata к dict[str, str] для безопасной сериализации
        metadata_dict: dict[str, str] | None = None
        if self.metadata:
            metadata_dict = {str(k): str(v) for k, v in self.metadata.items()}

        return {
            "id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "available": self._available,
            "metadata": metadata_dict,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | bool | dict | None]) -> "Book":
        """
        Создаёт книгу из словаря.

        Аргументы:
            data: Словарь с данными книги

        Возвращает:
            Экземпляр Book
        """
        book_id = str(data.get("id", str(uuid4())))
        title = str(data["title"])
        author = str(data["author"])
        available = bool(data.get("available", True))
        isbn = str(data["isbn"]) if data.get("isbn") else None

        # Безопасное получение metadata с приведением типов
        metadata: dict[str, str] | None = None
        raw_metadata = data.get("metadata")
        if isinstance(raw_metadata, dict):
            metadata = {str(k): str(v) for k, v in raw_metadata.items()}

        return cls(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            metadata=metadata,
            available=available,
        )

    def __str__(self):
        return f"Книга (id: {self.book_id}) '{self.title}' от {self.author} - {'доступна' if self._available else 'недоступна'}"

    def __repr__(self):
        return f"Book(id={self.book_id}, title='{self.title}', author='{self.author}', available={'доступна' if self._available else 'недоступна'})"
