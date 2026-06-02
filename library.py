import json
from card import LibraryCard
from book import Book
from exceptions import (
    TransactionError,
    BorrowLimitReachedError,
    BookNotAvailableError,
    BookNotBorrowedError,
    DuplicateCardError,
    InvalidDataError,
)
from book_manager import BookManager
from card_manager import CardManager


class Library:
    """Фасад библиотечной системы, объединяющий управление книгами и картами."""

    def __init__(
        self,
        book_manager: BookManager | None = None,
        card_manager: CardManager | None = None,
    ) -> None:
        """
        Инициализация библиотеки.

        Аргументы:
            book_manager: Менеджер книг (создаётся новый если None)
            card_manager: Менеджер карт (создаётся новый если None)
        """
        self.book_manager: BookManager = (
            book_manager if book_manager is not None else BookManager()
        )
        self.card_manager: CardManager = (
            card_manager if card_manager is not None else CardManager()
        )

    # ========== Управление книгами ==========

    def add_book(self, book: Book) -> None:
        """Добавляет книгу в библиотеку."""
        self.book_manager.add_book(book)

    def list_books(self) -> list[Book]:
        """Возвращает список всех книг в библиотеке."""
        return self.book_manager.list_books()

    def remove_book(self, book_id: str) -> None:
        """Удаляет книгу из библиотеки."""
        self.book_manager.remove_book(book_id)

    def find_books(
        self,
        title: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        available: bool | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Book]:
        """Ищет книги по критериям."""
        return self.book_manager.find_books(
            title=title,
            author=author,
            isbn=isbn,
            available=available,
            limit=limit,
            offset=offset,
        )

    # ========== Управление картами ==========

    def add_card(self, card: LibraryCard) -> None:
        """Добавляет читательскую карту."""
        self.card_manager.add_card(card)

    def list_cards(self) -> list[LibraryCard]:
        """Возвращает список всех карт."""
        return self.card_manager.list_cards()

    def remove_card(self, card_id: str) -> None:
        """Удаляет карту."""
        self.card_manager.remove_card(card_id)

    # ========== Транзакционные операции ==========

    def borrow(self, card_id: str, book_id: str) -> None:
        """
        Выдаёт книгу читателю (транзакционно).

        Аргументы:
            card_id: ID карты читателя
            book_id: ID книги

        Исключения:
            CardNotFoundError: Карта не найдена
            BookNotFoundError: Книга не найдена
            DuplicateCardError: Книга уже на карте
            BorrowLimitReachedError: Достигнут лимит выдачи
            BookNotAvailableError: Книга недоступна
            TransactionError: Сбой операции (с откатом)
        """
        card = self.card_manager.get_card(card_id)
        book = self.book_manager.get_book(book_id)

        # Валидация перед изменениями
        if card.has_borrowed(book_id):
            raise DuplicateCardError(f"Карта {card_id} уже содержит книгу {book_id}")

        if len(card.borrowed_books) >= card.borrow_limit:
            raise BorrowLimitReachedError(f"Карта {card_id} достигла лимита")

        if not book.is_available():
            raise BookNotAvailableError(f"Книга {book_id} недоступна")

        # Транзакция с откатом
        book_marked_unavailable = False
        try:
            book.borrow()
            book_marked_unavailable = True
            card.borrow(book)
        except (
            BorrowLimitReachedError,
            DuplicateCardError,
            BookNotAvailableError,
        ) as exc:
            if book_marked_unavailable:
                try:
                    book.return_book()  # Откат
                except Exception as rollback_exc:
                    raise TransactionError(
                        f"Не удалось выполнить откат книги {book_id}"
                    ) from rollback_exc
            raise TransactionError(
                f"Выдача не удалась для карты {card_id} и книги {book_id}"
            ) from exc

    def return_book(self, card_id: str, book_id: str) -> None:
        """
        Возвращает книгу от читателя (транзакционно).

        Аргументы:
            card_id: ID карты читателя
            book_id: ID книги

        Исключения:
            CardNotFoundError: Карта не найдена
            BookNotFoundError: Книга не найдена
            BookNotBorrowedError: Книга не была выдана на эту карту
            TransactionError: Сбой операции (с восстановлением)
        """
        card = self.card_manager.get_card(card_id)
        book = self.book_manager.get_book(book_id)

        if not card.has_borrowed(book_id):
            raise BookNotBorrowedError(f"Книга {book_id} не выдана карте {card_id}")

        removed_from_card = False
        try:
            card.return_book(book_id)
            removed_from_card = True
            book.return_book()
        except Exception as exc:
            if removed_from_card:
                try:
                    card._borrowed[book_id] = book  # Восстановление
                except Exception as restore_exc:
                    raise TransactionError() from restore_exc
                raise TransactionError() from exc

    def find_books_by_reader(self, card_id: str) -> list[Book]:
        """
        Возвращает список книг, выданных на конкретную карту.

        Аргументы:
            card_id: ID карты читателя

        Возвращает:
            Список книг (может быть пустым)

        Исключения:
            CardNotFoundError: Если карта не найдена
        """
        card = self.card_manager.get_card(card_id)
        return list(card.borrowed_books.values())

    def find_reader_by_book(self, book_id: str) -> str | None:
        """
        Находит читателя (ID карты), у которого находится книга.

        Аргументы:
            book_id: ID книги

        Возвращает:
            ID карты или None, если книга никому не выдана
        """
        for card in self.card_manager.list_cards():
            if card.has_borrowed(book_id):
                return card.card_id
        return None

    def get_borrowed_count(self, card_id: str) -> int:
        """Возвращает количество книг, выданных на карту."""
        card = self.card_manager.get_card(card_id)
        return len(card.borrowed_books)

    def get_available_books_count(self) -> int:
        """Возвращает количество доступных книг в библиотеке."""
        return sum(1 for book in self.book_manager.list_books() if book.is_available())

    # ========== Сериализация в JSON ==========

    def save_to_json(self, path: str) -> None:
        """
        Сохраняет состояние библиотеки в JSON файл.

        Аргументы:
            path: Путь к файлу

        Исключения:
            IOError: При ошибке записи файла
        """
        data = {
            "books": self.book_manager.to_dict(),
            "cards": self.card_manager.to_dict(),
            "version": "1.0",
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_json(self, path: str) -> None:
        """
        Загружает состояние библиотеки из JSON файла с проверкой целостности.

        Аргументы:
            path: Путь к файлу

        Исключения:
            InvalidDataError: Если файл повреждён или содержит несоответствия
            FileNotFoundError: Если файл не найден
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise InvalidDataError(f"Файл {path} не найден")
        except json.JSONDecodeError as e:
            raise InvalidDataError(f"Файл {path} содержит некорректный JSON: {e}")

        version = data.get("version")
        if version and version != "1.0":
            print(f"Предупреждение: Версия файла {version}, ожидалась 1.0")

        if "books" not in data or "cards" not in data:
            raise InvalidDataError(
                "JSON файл не содержит обязательных полей 'books' и 'cards'"
            )

        # Загружаем книги
        temp_book_manager = BookManager.from_dict(data["books"])

        # Загружаем карты с проверкой ссылок на книги
        temp_card_manager = CardManager.from_dict(
            data["cards"], book_collection=temp_book_manager.books
        )

        # Проверка целостности данных
        for card in temp_card_manager.cards.values():
            for book_id in card.borrowed_books:
                if book_id not in temp_book_manager.books:
                    raise InvalidDataError(
                        f"Несогласованные данные: Книга {book_id} выдана, но не найдена в коллекции"
                    )

        self.book_manager = temp_book_manager
        self.card_manager = temp_card_manager

    def __repr__(self):
        return (
            f"Library(книг: {len(self.book_manager)}, карт: {len(self.card_manager)})"
        )
