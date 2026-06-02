from book import Book
from card import LibraryCard
from exceptions import CardNotFoundError, DuplicateCardError, CardHasBorrowedBooks


class CardManager:
    """Управляет коллекцией читательских карт."""

    def __init__(self) -> None:
        """Инициализирует пустой менеджер карт."""
        self.cards: dict[str, LibraryCard] = {}

    def create_card(self, owner: str) -> LibraryCard:
        """
        Создаёт новую карту (без добавления в менеджер).

        Аргументы:
            owner: Владелец карты

        Возвращает:
            Новый экземпляр LibraryCard
        """
        return LibraryCard(owner=owner)

    def add_card(self, card: LibraryCard, overwrite: bool = False) -> None:
        """
        Добавляет карту в менеджер.

        Аргументы:
            card: Карта для добавления
            overwrite: Если True, перезаписывает существующую карту

        Исключения:
            DuplicateCardError: Если карта с таким ID уже существует и overwrite=False
        """
        if card.card_id not in self.cards or overwrite:
            self.cards[card.card_id] = card
        else:
            raise DuplicateCardError(f"Карта с ID {card.card_id} уже существует")

    def remove_card(self, card_id: str) -> None:
        """
        Удаляет карту из менеджера.

        Аргументы:
            card_id: ID карты для удаления

        Исключения:
            CardNotFoundError: Если карта не найдена
            CardHasBorrowedBooks: Если на карте есть выданные книги
        """
        card = self.cards.get(card_id)
        if card is not None:
            if not card.borrowed_books:
                self.cards.pop(card_id, None)
            else:
                raise CardHasBorrowedBooks(
                    f"Нельзя удалить карту {card_id}, на ней {len(card.borrowed_books)} книг"
                )
        else:
            raise CardNotFoundError(f"Карта с ID {card_id} не найдена")

    def get_card(self, card_id: str) -> LibraryCard:
        """
        Возвращает карту по ID.

        Аргументы:
            card_id: ID карты

        Возвращает:
            Карту

        Исключения:
            CardNotFoundError: Если карта не найдена
        """
        card = self.cards.get(card_id)
        if card is not None:
            return card
        raise CardNotFoundError(f"Карта с ID {card_id} не найдена")

    def list_cards(self) -> list[LibraryCard]:
        """Возвращает список всех карт в менеджере."""
        return list(self.cards.values())

    def to_dict(self) -> list[dict]:
        """Преобразует все карты в список словарей для сериализации."""
        return [card.to_dict() for card in self.cards.values()]

    @classmethod
    def from_dict(
        cls, data: list[dict], book_collection: dict[str, Book] | None = None
    ) -> "CardManager":
        """
        Создаёт CardManager из списка словарей.

        Аргументы:
            data: Список словарей с данными карт
            book_collection: Коллекция книг для восстановления ссылок

        Возвращает:
            Новый экземпляр CardManager с загруженными картами
        """
        mgr = cls()
        for cdata in data:
            card = LibraryCard.from_dict(cdata, book_collection)
            mgr.add_card(card, overwrite=True)
        return mgr

    def __len__(self) -> int:
        """Возвращает количество карт в менеджере."""
        return len(self.cards)

    def __contains__(self, card_id: str) -> bool:
        """Проверяет, существует ли карта с указанным ID."""
        return card_id in self.cards

    def __repr__(self) -> str:
        return f"CardManager({len(self.cards)} карт)"
