from __future__ import annotations
from uuid import uuid4
from book import Book
from exceptions import BookNotBorrowedError, BorrowLimitReachedError, DuplicateCardError


class LibraryCard:
    """Представляет читательский билет."""

    def __init__(
        self,
        owner: str,
        card_id: str | None = None,
        borrowed: dict[str, Book] | None = None,
        borrow_limit: int = 5,
    ) -> None:
        """
        Инициализация читательской карты.

        Аргументы:
            owner: Владелец карты
            card_id: Уникальный ID (генерируется автоматически если None)
            borrowed: Словарь выданных книг (создаётся новый если None)
            borrow_limit: Максимальное количество книг, которое можно взять
        """
        self.card_id: str = card_id if card_id is not None else str(uuid4())
        self.owner: str = owner
        self._borrowed: dict[str, Book] = borrowed if borrowed is not None else {}
        self.borrow_limit: int = borrow_limit

    @property
    def borrowed_books(self) -> dict[str, Book]:
        """
        Возвращает словарь выданных книг (только для чтения).
        Возвращается копия, чтобы предотвратить внешнее изменение.
        """
        return self._borrowed.copy()

    def borrow(self, book: Book) -> None:
        """
        Добавляет книгу на карту.

        Аргументы:
            book: Книга для выдачи

        Исключения:
            BorrowLimitReachedError: Если достигнут лимит
            DuplicateCardError: Если книга уже есть на карте
        """
        if len(self._borrowed) >= self.borrow_limit:
            raise BorrowLimitReachedError(
                f"Достигнут лимит выдачи ({self.borrow_limit})"
            )

        if book.book_id in self._borrowed:
            raise DuplicateCardError(f"Книга {book.book_id} уже на карте")

        self._borrowed[book.book_id] = book

    def return_book(self, book_id: str) -> None:
        """
        Удаляет книгу с карты.

        Аргументы:
            book_id: ID книги для возврата

        Исключения:
            BookNotBorrowedError: Если книга не была взята на эту карту
        """
        if book_id not in self._borrowed:
            raise BookNotBorrowedError(f"Книга {book_id} не выдана на эту карту")

        del self._borrowed[book_id]

    def list_borrowed(self) -> list[Book]:
        """Возвращает список выданных книг."""
        return list(self._borrowed.values())

    def has_borrowed(self, book_id: str) -> bool:
        """Проверяет, взята ли книга на этой карте."""
        return book_id in self._borrowed

    def to_dict(self) -> dict:
        """Преобразует карту в словарь для сериализации."""
        return {
            "card_id": self.card_id,
            "owner": self.owner,
            "borrowed": list(self._borrowed.keys()),
            "borrow_limit": self.borrow_limit,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        book_collection: dict[str, Book] | None = None,
    ) -> "LibraryCard":
        """
        Создаёт карту из словаря.

        Аргументы:
            data: Словарь с данными карты
            book_collection: Коллекция книг для восстановления ссылок на выданные книги

        Возвращает:
            Экземпляр LibraryCard

        Исключения:
            ValueError: Если book_collection передан и книга не найдена
        """
        card_id = str(data["card_id"])
        owner = str(data["owner"])
        borrowed_ids = data.get("borrowed", [])
        borrow_limit = data.get("borrow_limit", 5)

        card = cls(card_id=card_id, owner=owner, borrow_limit=borrow_limit)

        if book_collection:
            for book_id in borrowed_ids:
                if book_id in book_collection:
                    card._borrowed[book_id] = book_collection[book_id]
                else:
                    raise ValueError(f"Книга {book_id} не найдена в коллекции")
        return card

    def __str__(self):
        return f"Карта: {self.card_id}, владелец: {self.owner}, выдано книг: {len(self._borrowed)}, лимит: {self.borrow_limit}"

    def __repr__(self):
        return f"LibraryCard(id={self.card_id}, owner='{self.owner}', borrowed={len(self._borrowed)}, limit={self.borrow_limit})"
