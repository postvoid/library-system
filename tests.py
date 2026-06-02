"""
Тесты для библиотечной системы с использованием pytest.
Запуск: pytest tests.py -v
"""

import json
import tempfile
import pytest

from book import Book
from card import LibraryCard
from library import Library
from book_manager import BookManager
from card_manager import CardManager
from exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    BorrowLimitReachedError,
    BookNotBorrowedError,
    CardNotFoundError,
    DuplicateBookError,
    DuplicateCardError,
    CardHasBorrowedBooks,
    TransactionError,
    InvalidDataError,
)

# ========== Фикстуры ==========


@pytest.fixture
def sample_book():
    """Создаёт тестовую книгу."""
    return Book(title="Война и мир", author="Толстой Л.Н.")


@pytest.fixture
def sample_book_with_isbn():
    """Создаёт тестовую книгу с ISBN."""
    return Book(
        title="Преступление и наказание",
        author="Достоевский Ф.М.",
        isbn="978-5-17-118919-8",
        metadata={"год": "1866", "жанр": "роман"},
    )


@pytest.fixture
def sample_card():
    """Создаёт тестовую читательскую карту."""
    return LibraryCard(owner="Иван Петров")


@pytest.fixture
def book_manager():
    """Создаёт менеджер книг с двумя тестовыми книгами."""
    bm = BookManager()
    bm.add_book(Book(title="Книга 1", author="Автор 1"))
    bm.add_book(Book(title="Книга 2", author="Автор 2"))
    return bm


@pytest.fixture
def card_manager():
    """Создаёт менеджер карт с двумя тестовыми картами."""
    cm = CardManager()
    cm.add_card(LibraryCard(owner="Читатель 1"))
    cm.add_card(LibraryCard(owner="Читатель 2"))
    return cm


@pytest.fixture
def library(book_manager, card_manager):
    """Создаёт библиотеку с менеджерами."""
    return Library(book_manager=book_manager, card_manager=card_manager)


@pytest.fixture
def library_with_borrowed_book(library, sample_card, sample_book):
    """Создаёт библиотеку с выданной книгой."""
    library.add_card(sample_card)
    library.add_book(sample_book)
    library.borrow(sample_card.card_id, sample_book.book_id)
    return library, sample_card, sample_book


# ========== Тесты для класса Book ==========


class TestBook:
    """Тесты для класса Book."""

    def test_create_book_success(self):
        """Тест успешного создания книги."""
        book = Book(title="1984", author="Оруэлл")
        assert book.title == "1984"
        assert book.author == "Оруэлл"
        assert book.is_available() is True
        assert book.book_id is not None

    def test_create_book_empty_title_raises_error(self):
        """Тест: создание книги без названия вызывает ошибку."""
        with pytest.raises(ValueError, match="Название книги обязательно"):
            Book(title="", author="Автор")

    def test_create_book_empty_author_raises_error(self):
        """Тест: создание книги без автора вызывает ошибку."""
        with pytest.raises(ValueError, match="Автор книги обязателен"):
            Book(title="Название", author="")

    def test_borrow_available_book(self, sample_book):
        """Тест: выдача доступной книги."""
        sample_book.borrow()
        assert sample_book.is_available() is False

    def test_borrow_unavailable_book_raises_error(self, sample_book):
        """Тест: выдача недоступной книги вызывает ошибку."""
        sample_book.borrow()
        with pytest.raises(BookNotAvailableError):
            sample_book.borrow()

    def test_return_borrowed_book(self, sample_book):
        """Тест: возврат выданной книги."""
        sample_book.borrow()
        sample_book.return_book()
        assert sample_book.is_available() is True

    def test_return_available_book_raises_error(self, sample_book):
        """Тест: возврат доступной книги вызывает ошибку."""
        with pytest.raises(BookNotAvailableError, match="не была выдана"):
            sample_book.return_book()

    def test_to_dict_contains_all_fields(self, sample_book_with_isbn):
        """Тест: to_dict содержит все поля."""
        book_dict = sample_book_with_isbn.to_dict()
        assert "id" in book_dict
        assert "title" in book_dict
        assert "author" in book_dict
        assert "isbn" in book_dict
        assert "available" in book_dict
        assert "metadata" in book_dict
        assert book_dict["title"] == "Преступление и наказание"
        assert book_dict["isbn"] == "978-5-17-118919-8"

    def test_from_dict_restores_book(self, sample_book_with_isbn):
        """Тест: from_dict восстанавливает книгу."""
        book_dict = sample_book_with_isbn.to_dict()
        restored_book = Book.from_dict(book_dict)
        assert restored_book.book_id == sample_book_with_isbn.book_id
        assert restored_book.title == sample_book_with_isbn.title
        assert restored_book.author == sample_book_with_isbn.author
        assert restored_book.isbn == sample_book_with_isbn.isbn
        assert restored_book.is_available() == sample_book_with_isbn.is_available()

    def test_from_dict_handles_metadata_safely(self):
        """Тест: from_dict безопасно обрабатывает metadata разных типов."""
        book_dict = {
            "id": "test-123",
            "title": "Тест",
            "author": "Тестер",
            "available": True,
            "metadata": {"key1": "value1", "key2": "value2"},
        }
        book = Book.from_dict(book_dict)
        assert book.metadata == {"key1": "value1", "key2": "value2"}

    def test_from_dict_handles_none_metadata(self):
        """Тест: from_dict корректно обрабатывает None в metadata."""
        book_dict = {
            "id": "test-123",
            "title": "Тест",
            "author": "Тестер",
            "available": True,
            "metadata": None,
        }
        book = Book.from_dict(book_dict)
        assert book.metadata is None or book.metadata == {}


# ========== Тесты для класса LibraryCard ==========


class TestLibraryCard:
    """Тесты для класса LibraryCard."""

    def test_create_card_success(self):
        """Тест успешного создания карты."""
        card = LibraryCard(owner="Мария Смирнова")
        assert card.owner == "Мария Смирнова"
        assert card.borrow_limit == 5
        assert len(card.borrowed_books) == 0

    def test_borrow_book_success(self, sample_card, sample_book):
        """Тест: добавление книги на карту."""
        sample_card.borrow(sample_book)
        assert sample_card.has_borrowed(sample_book.book_id) is True
        assert len(sample_card.borrowed_books) == 1

    def test_borrow_same_book_twice_raises_error(self, sample_card, sample_book):
        """Тест: повторное добавление той же книги вызывает ошибку."""
        sample_card.borrow(sample_book)
        with pytest.raises(DuplicateCardError):
            sample_card.borrow(sample_book)

    def test_borrow_exceeds_limit_raises_error(self, sample_card):
        """Тест: превышение лимита выдачи вызывает ошибку."""
        # Создаём 6 книг (лимит 5)
        for i in range(5):
            book = Book(title=f"Книга {i}", author="Автор")
            sample_card.borrow(book)

        sixth_book = Book(title="Шестая книга", author="Автор")
        with pytest.raises(BorrowLimitReachedError):
            sample_card.borrow(sixth_book)

    def test_return_book_success(self, sample_card, sample_book):
        """Тест: удаление книги с карты."""
        sample_card.borrow(sample_book)
        sample_card.return_book(sample_book.book_id)
        assert sample_card.has_borrowed(sample_book.book_id) is False

    def test_return_not_borrowed_book_raises_error(self, sample_card, sample_book):
        """Тест: возврат невыданной книги вызывает ошибку."""
        with pytest.raises(BookNotBorrowedError):
            sample_card.return_book(sample_book.book_id)

    def test_borrowed_books_property_returns_copy(self, sample_card, sample_book):
        """Тест: borrowed_books возвращает копию, а не оригинал."""
        sample_card.borrow(sample_book)
        borrowed = sample_card.borrowed_books
        assert len(borrowed) == 1
        # Изменение копии не влияет на оригинал
        borrowed.clear()
        assert len(sample_card.borrowed_books) == 1

    def test_to_dict_contains_borrowed_ids(self, sample_card, sample_book):
        """Тест: to_dict содержит ID выданных книг."""
        sample_card.borrow(sample_book)
        card_dict = sample_card.to_dict()
        assert card_dict["card_id"] == sample_card.card_id
        assert card_dict["owner"] == sample_card.owner
        assert sample_book.book_id in card_dict["borrowed"]


# ========== Тесты для BookManager ==========


class TestBookManager:
    """Тесты для BookManager."""

    def test_add_book_success(self, book_manager, sample_book):
        """Тест: добавление книги в менеджер."""
        initial_count = len(book_manager)
        book_manager.add_book(sample_book)
        assert len(book_manager) == initial_count + 1
        assert sample_book.book_id in book_manager

    def test_add_duplicate_book_raises_error(self, book_manager):
        """Тест: добавление дубликата книги вызывает ошибку."""
        books = book_manager.list_books()
        duplicate = books[0]
        with pytest.raises(DuplicateBookError):
            book_manager.add_book(duplicate)

    def test_add_book_overwrite_success(self, book_manager):
        """Тест: перезапись книги с overwrite=True."""
        books = book_manager.list_books()
        original_book = books[0]
        new_book = Book(
            title="Новое название", author="Новый автор", book_id=original_book.book_id
        )
        book_manager.add_book(new_book, overwrite=True)
        updated_book = book_manager.get_book(original_book.book_id)
        assert updated_book.title == "Новое название"

    def test_remove_book_success(self, book_manager):
        """Тест: удаление книги из менеджера."""
        books = book_manager.list_books()
        book_id = books[0].book_id
        book_manager.remove_book(book_id)
        with pytest.raises(BookNotFoundError):
            book_manager.get_book(book_id)

    def test_remove_nonexistent_book_raises_error(self, book_manager):
        """Тест: удаление несуществующей книги вызывает ошибку."""
        with pytest.raises(BookNotFoundError):
            book_manager.remove_book("nonexistent-id")

    def test_find_books_by_title(self, book_manager):
        """Тест: поиск книг по названию."""
        book_manager.add_book(Book(title="Уникальное название", author="Автор"))
        results = book_manager.find_books(title="Уникальное")
        assert len(results) == 1
        assert "Уникальное название" in results[0].title

    def test_find_books_by_author(self, book_manager):
        """Тест: поиск книг по автору."""
        book_manager.add_book(Book(title="Название", author="Уникальный автор"))
        results = book_manager.find_books(author="Уникальный")
        assert len(results) == 1
        assert results[0].author == "Уникальный автор"

    def test_find_books_with_pagination(self, book_manager):
        """Тест: пагинация результатов поиска."""
        # Добавляем ещё книги
        for i in range(10):
            book_manager.add_book(Book(title=f"Книга {i}", author="Один автор"))

        results = book_manager.find_books(author="Один автор", limit=3, offset=2)
        assert len(results) == 3

    def test_find_books_filter_by_availability(self, book_manager):
        """Тест: фильтрация по доступности."""
        books = book_manager.list_books()
        books[0].borrow()

        available_results = book_manager.find_books(available=True)
        unavailable_results = book_manager.find_books(available=False)

        # Хотя бы одна книга недоступна
        assert len(unavailable_results) >= 1
        # Все результаты unavailable_results действительно недоступны
        for book in unavailable_results:
            assert book.is_available() is False

    def test_register_book_creates_and_adds(self, book_manager):
        """Тест: register_book создаёт и добавляет книгу за один шаг."""
        book = book_manager.register_book("Новая книга", "Новый автор")
        assert book.book_id in book_manager
        assert book.title == "Новая книга"

    def test_to_dict_returns_list_of_dicts(self, book_manager):
        """Тест: to_dict возвращает список словарей."""
        result = book_manager.to_dict()
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)
            assert "id" in result[0]
            assert "title" in result[0]

    def test_from_dict_restores_manager(self, book_manager):
        """Тест: from_dict восстанавливает менеджер из словаря."""
        data = book_manager.to_dict()
        restored_manager = BookManager.from_dict(data)
        assert len(restored_manager) == len(book_manager)

        original_books = {b.book_id: b.title for b in book_manager.list_books()}
        restored_books = {b.book_id: b.title for b in restored_manager.list_books()}
        assert original_books == restored_books


# ========== Тесты для CardManager ==========


class TestCardManager:
    """Тесты для CardManager."""

    def test_add_card_success(self, card_manager, sample_card):
        """Тест: добавление карты в менеджер."""
        initial_count = len(card_manager)
        card_manager.add_card(sample_card)
        assert len(card_manager) == initial_count + 1

    def test_remove_card_without_books_success(self, card_manager):
        """Тест: удаление карты без книг."""
        cards = card_manager.list_cards()
        card_id = cards[0].card_id
        card_manager.remove_card(card_id)
        with pytest.raises(CardNotFoundError):
            card_manager.get_card(card_id)

    def test_remove_card_with_borrowed_books_raises_error(
        self, card_manager, sample_book
    ):
        """Тест: удаление карты с выданными книгами вызывает ошибку."""
        cards = card_manager.list_cards()
        card = cards[0]
        card.borrow(sample_book)

        with pytest.raises(CardHasBorrowedBooks):
            card_manager.remove_card(card.card_id)

    def test_get_card_success(self, card_manager):
        """Тест: получение карты по ID."""
        cards = card_manager.list_cards()
        expected_card = cards[0]
        actual_card = card_manager.get_card(expected_card.card_id)
        assert actual_card.card_id == expected_card.card_id

    def test_get_nonexistent_card_raises_error(self, card_manager):
        """Тест: получение несуществующей карты вызывает ошибку."""
        with pytest.raises(CardNotFoundError):
            card_manager.get_card("nonexistent-id")


# ========== Тесты для Library (фасад) ==========


class TestLibrary:
    """Тесты для фасада Library."""

    def test_add_and_list_books(self, library, sample_book):
        """Тест: добавление и получение списка книг."""
        initial_count = len(library.list_books())
        library.add_book(sample_book)
        assert len(library.list_books()) == initial_count + 1

    def test_remove_book_success(self, library, sample_book):
        """Тест: удаление книги из библиотеки."""
        library.add_book(sample_book)
        library.remove_book(sample_book.book_id)
        with pytest.raises(BookNotFoundError):
            library.book_manager.get_book(sample_book.book_id)

    def test_borrow_book_success(self, library, sample_card, sample_book):
        """Тест: успешная выдача книги."""
        library.add_card(sample_card)
        library.add_book(sample_book)

        library.borrow(sample_card.card_id, sample_book.book_id)

        assert sample_book.is_available() is False
        assert sample_card.has_borrowed(sample_book.book_id) is True

    def test_borrow_already_borrowed_book_raises_error(
        self, library_with_borrowed_book
    ):
        """Тест: выдача уже выданной книги вызывает ошибку."""
        library, card, book = library_with_borrowed_book

        # Пытаемся выдать ту же книгу снова
        with pytest.raises(TransactionError):
            library.borrow(card.card_id, book.book_id)

    def test_borrow_when_card_limit_reached_raises_error(self, library, sample_card):
        """Тест: выдача при достижении лимита карты вызывает ошибку."""
        library.add_card(sample_card)

        # Добавляем 5 книг (лимит карты)
        books = []
        for i in range(5):
            book = Book(title=f"Книга {i}", author="Автор")
            library.add_book(book)
            library.borrow(sample_card.card_id, book.book_id)
            books.append(book)

        # Пытаемся взять шестую книгу
        sixth_book = Book(title="Шестая книга", author="Автор")
        library.add_book(sixth_book)

        with pytest.raises(TransactionError):
            library.borrow(sample_card.card_id, sixth_book.book_id)

    def test_return_book_success(self, library_with_borrowed_book):
        """Тест: успешный возврат книги."""
        library, card, book = library_with_borrowed_book
        library.return_book(card.card_id, book.book_id)

        assert book.is_available() is True
        assert card.has_borrowed(book.book_id) is False

    def test_return_not_borrowed_book_raises_error(
        self, library, sample_card, sample_book
    ):
        """Тест: возврат невыданной книги вызывает ошибку."""
        library.add_card(sample_card)
        library.add_book(sample_book)

        with pytest.raises(BookNotBorrowedError):
            library.return_book(sample_card.card_id, sample_book.book_id)

    def test_find_books_by_reader(self, library_with_borrowed_book):
        """Тест: поиск книг по читателю."""
        library, card, book = library_with_borrowed_book
        reader_books = library.find_books_by_reader(card.card_id)

        assert len(reader_books) == 1
        assert reader_books[0].book_id == book.book_id

    def test_find_reader_by_book(self, library_with_borrowed_book):
        """Тест: поиск читателя по книге."""
        library, card, book = library_with_borrowed_book
        found_card_id = library.find_reader_by_book(book.book_id)

        assert found_card_id == card.card_id

    def test_get_borrowed_count(self, library, sample_card):
        """Тест: получение количества выданных книг."""
        library.add_card(sample_card)

        book1 = Book(title="Книга 1", author="Автор")
        book2 = Book(title="Книга 2", author="Автор")
        library.add_book(book1)
        library.add_book(book2)

        assert library.get_borrowed_count(sample_card.card_id) == 0

        library.borrow(sample_card.card_id, book1.book_id)
        assert library.get_borrowed_count(sample_card.card_id) == 1

        library.borrow(sample_card.card_id, book2.book_id)
        assert library.get_borrowed_count(sample_card.card_id) == 2

    def test_get_available_books_count(self, library, sample_card):
        """Тест: получение количества доступных книг."""
        book1 = Book(title="Книга 1", author="Автор")
        book2 = Book(title="Книга 2", author="Автор")
        library.add_book(book1)
        library.add_book(book2)
        library.add_card(sample_card)

        assert library.get_available_books_count() == 2

        library.borrow(sample_card.card_id, book1.book_id)
        assert library.get_available_books_count() == 1


# ========== Тесты для JSON сериализации ==========


class TestJSONSerialization:
    """Тесты для сохранения и загрузки JSON."""

    def test_save_and_load_json(self, library, sample_card, sample_book):
        """Тест: сохранение и загрузка состояния библиотеки."""
        library.add_card(sample_card)
        library.add_book(sample_book)
        library.borrow(sample_card.card_id, sample_book.book_id)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            library.save_to_json(temp_path)

            new_library = Library()
            new_library.load_from_json(temp_path)

            assert len(new_library.list_books()) == len(library.list_books())
            assert len(new_library.list_cards()) == len(library.list_cards())

            # Проверяем, что книга выдана
            new_card = new_library.list_cards()[0]
            assert len(new_card.borrowed_books) == 1

        finally:
            import os

            os.unlink(temp_path)

    def test_load_from_nonexistent_file_raises_error(self):
        """Тест: загрузка из несуществующего файла вызывает ошибку."""
        library = Library()
        with pytest.raises(InvalidDataError, match="не найден"):
            library.load_from_json("nonexistent_file_12345.json")

    def test_load_from_invalid_json_raises_error(self):
        """Тест: загрузка из повреждённого JSON вызывает ошибку."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json,}')
            temp_path = f.name

        library = Library()
        try:
            with pytest.raises(InvalidDataError, match="некорректный JSON"):
                library.load_from_json(temp_path)
        finally:
            import os

            os.unlink(temp_path)

    def test_load_from_json_missing_fields_raises_error(self):
        """Тест: загрузка JSON без обязательных полей вызывает ошибку."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"version": "1.0"}, f)
            temp_path = f.name

        library = Library()
        try:
            with pytest.raises(
                InvalidDataError, match="не содержит обязательных полей"
            ):
                library.load_from_json(temp_path)
        finally:
            import os

            os.unlink(temp_path)


# ========== Тесты для граничных случаев ==========


class TestEdgeCases:
    """Тесты для граничных случаев."""

    def test_borrow_nonexistent_book_raises_error(self, library, sample_card):
        """Тест: выдача несуществующей книги вызывает ошибку."""
        library.add_card(sample_card)
        with pytest.raises(BookNotFoundError):
            library.borrow(sample_card.card_id, "nonexistent-id")

    def test_borrow_with_nonexistent_card_raises_error(self, library, sample_book):
        """Тест: выдача по несуществующей карте вызывает ошибку."""
        library.add_book(sample_book)
        with pytest.raises(CardNotFoundError):
            library.borrow("nonexistent-card", sample_book.book_id)

    def test_return_book_with_wrong_card_raises_error(self, library_with_borrowed_book):
        """Тест: возврат книги с чужой карты вызывает ошибку."""
        library, correct_card, book = library_with_borrowed_book

        # Создаём другую карту
        other_card = LibraryCard(owner="Другой читатель")
        library.add_card(other_card)

        with pytest.raises(BookNotBorrowedError):
            library.return_book(other_card.card_id, book.book_id)

    def test_find_books_empty_result(self, library):
        """Тест: поиск книг с пустым результатом."""
        results = library.find_books(title="Несуществующее название")
        assert results == []

    def test_remove_book_that_is_borrowed_raises_error(
        self, library_with_borrowed_book
    ):
        """Тест: удаление выданной книги вызывает ошибку."""
        library, card, book = library_with_borrowed_book
        with pytest.raises(BookNotAvailableError):
            library.remove_book(book.book_id)


# ========== Запуск тестов ==========
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
