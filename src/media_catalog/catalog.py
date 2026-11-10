"""Каталог с поиском по словарному индексу."""

from collections.abc import Iterable, Iterator

from media_catalog.errors import DuplicateIdError, InvalidMediaError, ItemNotFoundError
from media_catalog.models import Media


class Catalog:
    """Хранит медиаобъекты в словаре по ID и сохраняет порядок добавления."""

    def __init__(self, items: Iterable[Media] = ()) -> None:
        """Создаёт каталог и добавляет в него переданные объекты с проверкой ID."""
        self._items: dict[str, Media] = {}
        for item in items:
            self.add(item)

    def add(self, item: Media) -> None:
        """Добавляет Media в каталог. При повторном ID вызывает DuplicateIdError."""
        if not isinstance(item, Media):
            raise InvalidMediaError("Каталог принимает только Media")
        if item.id in self._items:
            raise DuplicateIdError(f"Дублирующийся ID: {item.id}")
        self._items[item.id] = item

    def get(self, item_id: str) -> Media:
        """Возвращает объект по ID. Если ID отсутствует, вызывает ItemNotFoundError."""
        try:
            return self._items[item_id]
        except KeyError as error:
            raise ItemNotFoundError(f"ID отсутствует: {item_id}") from error

    def remove(self, item_id: str) -> Media:
        """Удаляет и возвращает объект по ID. Если ID отсутствует, вызывает ItemNotFoundError."""
        item = self.get(item_id)
        del self._items[item_id]
        return item

    def find_by_category(self, category: str) -> list[Media]:
        """Возвращает отдельный список объектов с указанной категорией."""
        return [item for item in self if item.category == category]

    def find_by_name(self, query: str) -> list[Media]:
        """Возвращает объекты, в названиях которых есть запрос, без учёта регистра."""
        query = query.casefold()
        return [item for item in self if query in item.name.casefold()]

    def replace_all(self, items: Iterable[Media]) -> None:
        """Заменяет содержимое каталога, только если все новые объекты прошли проверку."""
        candidate = Catalog(items)
        self._items = candidate._items

    def __len__(self) -> int:
        """Возвращает количество объектов для len(catalog)."""
        return len(self._items)

    def __iter__(self) -> Iterator[Media]:
        """Возвращает итератор по копии коллекции в порядке добавления."""
        return iter(tuple(self._items.values()))

    def __contains__(self, item_id: str) -> bool:
        """Проверяет наличие ID для выражения item_id in catalog."""
        return item_id in self._items
