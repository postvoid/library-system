from __future__ import annotations
from book import Book
from exceptions import BookNotFoundError, DuplicateBookError, BookNotAvailableError


class BookManager:
    """Управляет коллекцией книг в библиотеке."""

    def __init__(self) -> None:
        """Инициализирует пустой менеджер книг."""
        self.books: dict[str, Book] = {}

    def create_book(self, title: str, author: str) -> Book:
        """
        Создаёт новую книгу (без добавления в менеджер).

        Аргументы:
            title: Название книги
            author: Автор книги

        Возвращает:
            Новый экземпляр Book
        """
        return Book(title=title, author=author)

    def add_book(self, book: Book, overwrite: bool = False) -> None:
        """
        Добавляет книгу в менеджер.

        Аргументы:
            book: Книга для добавления
            overwrite: Если True, перезаписывает существующую книгу

        Исключения:
            DuplicateBookError: Если книга с таким ID уже существует и overwrite=False
        """
        if book.book_id not in self.books or overwrite:
            self.books[book.book_id] = book
        else:
            raise DuplicateBookError(f"Книга с ID {book.book_id} уже существует")

    def register_book(self, title: str, author: str) -> Book:
        """
        Создаёт и регистрирует книгу за один шаг.

        Аргументы:
            title: Название книги
            author: Автор книги

        Возвращает:
            Созданную и зарегистрированную книгу
        """
        book = self.create_book(title, author)
        self.add_book(book)
        return book

    def remove_book(self, book_id: str) -> None:
        """
        Удаляет книгу из менеджера.

        Аргументы:
            book_id: ID книги для удаления

        Исключения:
            BookNotFoundError: Если книга не найдена
            BookNotAvailableError: Если книга выдана (недоступна)
        """
        book = self.books.get(book_id)
        if book is None:
            raise BookNotFoundError(f"Книга с ID {book_id} не найдена")

        if not book.is_available():
            raise BookNotAvailableError(f"Нельзя удалить выданную книгу {book_id}")

        self.books.pop(book_id, None)

    def get_book(self, book_id: str) -> Book:
        """
        Возвращает книгу по ID.

        Аргументы:
            book_id: ID книги

        Возвращает:
            Книгу

        Исключения:
            BookNotFoundError: Если книга не найдена
        """
        book = self.books.get(book_id)
        if book is None:
            raise BookNotFoundError(f"Книга с ID {book_id} не найдена")
        return book

    def list_books(self) -> list[Book]:
        """Возвращает список всех книг в менеджере."""
        return list(self.books.values())

    def find_books(
        self,
        title: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        available: bool | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Book]:
        """
        Ищет книги по заданным критериям.

        Аргументы:
            title: Часть названия для поиска
            author: Часть имени автора для поиска
            isbn: Часть ISBN для поиска
            available: Фильтр по доступности
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Возвращает:
            Список найденных книг (может быть пустым)
        """

        def normalize(s: str | None) -> str | None:
            """Нормализует строку для поиска (нижний регистр, убирает пробелы)."""
            return s.strip().lower() if s and s.strip() else None

        title_q = normalize(title)
        author_q = normalize(author)
        isbn_q = normalize(isbn)

        if offset < 0:
            offset = 0

        results: list[Book] = []

        for book in self.books.values():
            if available is not None and book.is_available() is not available:
                continue
            if title_q is not None:
                if not book.title or title_q not in book.title.lower():
                    continue
            if author_q is not None:
                if not book.author or author_q not in book.author.lower():
                    continue
            if isbn_q is not None:
                book_isbn = (book.isbn or "").lower()
                if isbn_q not in book_isbn:
                    continue
            results.append(book)

        if offset:
            results = results[offset:]
        if limit is not None:
            results = results[: max(0, limit)]

        return results

    def to_dict(self) -> list[dict[str, str | bool | dict[str, str] | None]]:
        """Преобразует все книги в список словарей для сериализации."""
        return [book.to_dict() for book in self.books.values()]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "BookManager":
        """
        Создаёт BookManager из списка словарей.

        Аргументы:
            data: Список словарей с данными книг

        Возвращает:
            Новый экземпляр BookManager с загруженными книгами
        """
        mgr = cls()
        for bdata in data:
            book = Book.from_dict(bdata)
            mgr.add_book(book, overwrite=True)
        return mgr

    def __len__(self) -> int:
        """Возвращает количество книг в менеджере."""
        return len(self.books)

    def __contains__(self, book_id: str) -> bool:
        """Проверяет, существует ли книга с указанным ID."""
        return book_id in self.books

    def __repr__(self):
        return f"BookManager({len(self.books)} книг)"
