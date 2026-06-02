class LibraryError(Exception):
    """Базовое исключение для ошибок библиотеки."""

    def __init__(
        self,
        error_message: str | None = None,
        card_id: str | None = None,
        book_id: str | None = None,
    ):
        super().__init__(error_message, card_id, book_id)


class BookNotAvailableError(LibraryError):
    """Выбрасывается при попытке взять недоступную книгу."""

    pass


class BorrowLimitReachedError(LibraryError):
    """Выбрасывается, когда достигнут лимит выдачи книг."""

    pass


class BookNotBorrowedError(LibraryError):
    """Выбрасывается при попытке вернуть книгу, которая не была взята."""

    pass


class BookNotFoundError(LibraryError):
    """Выбрасывается, когда книга не найдена в менеджере."""

    pass


class CardNotFoundError(LibraryError):
    """Выбрасывается, когда карта не найдена в менеджере."""

    pass


class DuplicateBookError(LibraryError):
    """Выбрасывается при попытке добавить дубликат книги."""

    pass


class DuplicateCardError(LibraryError):
    """Выбрасывается при попытке добавить дубликат карты."""

    pass


class CardHasBorrowedBooks(LibraryError):
    """Выбрасывается при попытке удалить карту с выданными книгами."""

    pass


class TransactionError(LibraryError):
    """Выбрасывается при сбое транзакции с откатом изменений."""

    pass


class InvalidDataError(LibraryError):
    """Выбрасывается при загрузке некорректных данных из JSON."""

    pass
