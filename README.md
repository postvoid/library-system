# 📚 Библиотечная система управления (Library Management System)

**Простая, но надёжная система для автоматизации работы библиотеки на Python. Поддерживает учёт книг, читательских билетов, выдачу/возврат книг с гарантией целостности данных (транзакции с откатом).**

## 🚀 Возможности

- **Управление книгами** – добавление, удаление, поиск по названию/автору/ISBN
- **Читательские билеты** – создание, удаление, контроль лимита выдачи (по умолчанию 5 книг)
- **Выдача и возврат** – атомарные операции с автоматическим откатом при сбоях
- **Поиск** – гибкие фильтры (пагинация, доступность, частичное совпадение)
- **Сохранение/загрузка** – JSON-сериализация с проверкой целостности данных

## 🛠 Технологии

- Python 3.10+ (аннотации типов и `| None`)
- Встроенные библиотеки: `json`, `uuid`
- Кастомные исключения для каждого сценария ошибок
- **pytest** – для тестирования

## 📦 Установка

```bash
git clone https://github.com/postvoid/library-system.git
cd library-system
```

Кроме `pytest` никаких внешних зависимостей не требуется — всё на стандартной библиотеке.

## 🏃 Быстрый старт

```python
from book import Book
from card import LibraryCard
from library import Library

# Создаём библиотеку
lib = Library()

# Добавляем книги
book1 = Book(title="Мастер и Маргарита", author="Булгаков")
book2 = Book(title="1984", author="Оруэлл", isbn="978-5-17-118919-8")
lib.add_book(book1)
lib.add_book(book2)

# Оформляем читательский билет
card = LibraryCard(owner="Иван Петров")
lib.add_card(card)

# Выдаём книгу
lib.borrow(card_id=card.card_id, book_id=book1.book_id)

# Смотрим, что у читателя
print(lib.find_books_by_reader(card.card_id))  # [Мастер и Маргарита]

# Сохраняем состояние
lib.save_to_json("library_backup.json")
```

## 📖 API

### Книги (`Book`)

```python
book = Book(title="Война и мир", author="Толстой", isbn="...")
book.borrow()          # выдать
book.return_book()     # вернуть
book.is_available()    # проверить доступность
```

### Читательские билеты (`LibraryCard`)

```python
card = LibraryCard(owner="Имя", borrow_limit=3)
card.borrow(book)      # добавить книгу на карту
card.return_book(id)   # удалить книгу с карты
card.list_borrowed()   # список взятых книг
```

### Библиотека (`Library` – фасад)

| Метод | Описание |
|-------|----------|
| `add_book(book)` | Добавить книгу |
| `remove_book(book_id)` | Удалить книгу (только если не выдана) |
| `add_card(card)` | Добавить читательский билет |
| `remove_card(card_id)` | Удалить билет (только если нет книг) |
| `borrow(card_id, book_id)` | Выдать книгу (с откатом при ошибке) |
| `return_book(card_id, book_id)` | Принять возврат |
| `find_books(title, author, isbn, available, limit, offset)` | Поиск книг |
| `find_books_by_reader(card_id)` | Книги у читателя |
| `find_reader_by_book(book_id)` | Кто держит книгу |
| `save_to_json(path)` / `load_from_json(path)` | Сохранение/загрузка |

## ⚠️ Исключения

| Исключение | Когда возникает |
|------------|------------------|
| `BookNotFoundError` | Книга не найдена |
| `BookNotAvailableError` | Книга уже выдана |
| `BookNotBorrowedError` | Попытка вернуть невыданную книгу |
| `CardNotFoundError` | Карта не найдена |
| `BorrowLimitReachedError` | Лимит книг на руках превышен |
| `DuplicateBookError` | Добавление дубликата книги |
| `CardHasBorrowedBooks` | Удаление карты с книгами |
| `TransactionError` | Сбой операции (состояние откачено) |
| `InvalidDataError` | Повреждённый JSON при загрузке |

## 💾 Формат данных

Сохраняемый JSON-файл имеет структуру:

```json
{
  "version": "1.0",
  "books": [
    {
      "id": "...",
      "title": "...",
      "author": "...",
      "isbn": "...",
      "available": true,
      "metadata": {}
    }
  ],
  "cards": [
    {
      "card_id": "...",
      "owner": "...",
      "borrowed": ["book_id1"],
      "borrow_limit": 5
    }
  ]
}
```

---

## 🧪 Тестирование с pytest

В файле `tests.py` приведены примеры тестирования.

```bash
# Установка pytest
pip install pytest pytest-cov

# Запуск тестов
pytest tests.py -v

# Запуск с отчётом о покрытии
pytest tests.py --cov=. --cov-report=term-missing
```

**Пример теста:**

```python
def test_borrow_available_book():
    lib = Library()
    book = Book("Title", "Author")
    card = LibraryCard("Owner")
    lib.add_book(book)
    lib.add_card(card)
    
    lib.borrow(card.card_id, book.book_id)
    assert not book.is_available()
    assert card.has_borrowed(book.book_id)

def test_borrow_unavailable_book():
    lib = Library()
    book = Book("Title", "Author", available=False)
    card = LibraryCard("Owner")
    lib.add_book(book)
    lib.add_card(card)
    
    with pytest.raises(BookNotAvailableError):
        lib.borrow(card.card_id, book.book_id)
```

## 📁 Структура проекта

```
library-system/
├── book.py               # Класс книги
├── book_manager.py       # Хранилище книг
├── card.py               # Читательский билет
├── card_manager.py       # Хранилище карт
├── library.py            # Фасад (главный класс)
├── example.py            # Пример использования
├── exceptions.py         # Все исключения
├── tests.py              # Тесты pytest
└── README.md
```

## 🔒 Принципы работы

- **Атомарность операций** – выдача и возврат обёрнуты в транзакции с откатом
- **Инкапсуляция** – внутренние поля (`_borrowed`, `_available`) защищены
- **Проверка согласованности** – при загрузке из JSON проверяются ссылки между книгами и картами
- **Информативные ошибки** – каждое исключение содержит пояснение
