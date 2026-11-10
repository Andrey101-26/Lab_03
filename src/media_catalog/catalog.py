"""Каталог с поиском по словарному индексу."""

from collections.abc import Iterable, Iterator

from media_catalog.errors import DuplicateIdError, InvalidMediaError, ItemNotFoundError
from media_catalog.models import Media


class Catalog:
    """Хранить объекты в порядке добавления; ID сравниваются точно."""

    def __init__(self, items: Iterable[Media] = ()) -> None:
        """Создать каталог и проверить начальные объекты."""
        self._items: dict[str, Media] = {}
        for item in items:
            self.add(item)

    def add(self, item: Media) -> None:
        """Добавить объект, запретив повторный ID."""
        if not isinstance(item, Media):
            raise InvalidMediaError("Каталог принимает только Media")
        if item.id in self._items:
            raise DuplicateIdError(f"Дублирующийся ID: {item.id}")
        self._items[item.id] = item

    def get(self, item_id: str) -> Media:
        """Найти объект по ID за среднее O(1)."""
        try:
            return self._items[item_id]
        except KeyError as error:
            raise ItemNotFoundError(f"ID отсутствует: {item_id}") from error

    def remove(self, item_id: str) -> Media:
        """Удалить и вернуть объект или сообщить об отсутствии."""
        item = self.get(item_id)
        del self._items[item_id]
        return item

    def find_by_category(self, category: str) -> list[Media]:
        """Вернуть новый список объектов с точно совпадающей категорией."""
        return [item for item in self if item.category == category]

    def find_by_name(self, query: str) -> list[Media]:
        """Найти подстроку в названии без учёта регистра за O(n)."""
        query = query.casefold()
        return [item for item in self if query in item.name.casefold()]

    def replace_all(self, items: Iterable[Media]) -> None:
        """Заменить содержимое после проверки всех новых объектов."""
        candidate = Catalog(items)
        self._items = candidate._items

    def __len__(self) -> int:
        """Вернуть число объектов."""
        return len(self._items)

    def __iter__(self) -> Iterator[Media]:
        """Перебирать снимок объектов в порядке добавления."""
        return iter(tuple(self._items.values()))

    def __contains__(self, item_id: str) -> bool:
        """Проверить наличие ID."""
        return item_id in self._items
