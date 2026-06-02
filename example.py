from library import Library
from book import Book
from card import LibraryCard

# Создаём библиотеку
lib = Library()

# Добавляем книги
book1 = Book(title="Мастер и Маргарита", author="Булгаков")
book2 = Book(title="Преступление и наказание", author="Достоевский")
lib.add_book(book1)
lib.add_book(book2)

# Добавляем читателя
card = LibraryCard(owner="Иван Петров")
lib.add_card(card)

# Выдаём книгу
lib.borrow(card.card_id, book1.book_id)

# Проверяем статистику
print(f"Книги у читателя: {lib.find_books_by_reader(card.card_id)}")
print(f"Доступных книг: {lib.get_available_books_count()}")

# Сохраняем и загружаем
lib.save_to_json("library_backup.json")

lib2 = Library()
lib2.load_from_json("library_backup.json")
print(f"Загружено книг: {len(lib2.list_books())}")
