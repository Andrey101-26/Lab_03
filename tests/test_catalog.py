"""Проверки операций каталога и протоколов."""

import pytest

from media_catalog.catalog import Catalog
from media_catalog.errors import DuplicateIdError, InvalidMediaError, ItemNotFoundError
from media_catalog.models import Media


def make_item(item_id: str, name: str = "Солярис", category: str = "фильм") -> Media:
    """Создать допустимый объект для теста."""
    return Media(item_id, name, category, 1972, "Автор", 90)


def test_add_get_remove() -> None:
    """Добавление, получение и удаление согласованы с индексом."""
    catalog = Catalog()
    item = make_item("1")
    assert catalog.add(item) is None
    assert catalog.get("1") is item
    assert len(catalog) == 1 and "1" in catalog
    assert catalog.remove("1") is item
    assert len(catalog) == 0 and "1" not in catalog
    assert catalog.find_by_category("фильм") == []


def test_duplicate_does_not_replace_original() -> None:
    """Дубликат не заменяет исходный объект."""
    original = make_item("1")
    catalog = Catalog([original])
    with pytest.raises(DuplicateIdError):
        catalog.add(make_item("1", "Другое имя"))
    assert list(catalog) == [original]


def test_missing_id_errors() -> None:
    """Обе операции с отсутствующим ID вызывают предметную ошибку."""
    catalog = Catalog()
    with pytest.raises(ItemNotFoundError):
        catalog.get("missing")
    with pytest.raises(ItemNotFoundError):
        catalog.remove("missing")


def test_search_and_independent_results() -> None:
    """Поиск имени не учитывает регистр, списки результатов независимы."""
    movie = make_item("1")
    song = make_item("2", "Соната", "музыка")
    catalog = Catalog([movie, song])
    assert catalog.find_by_name("СОЛЯ") == [movie]
    assert catalog.find_by_category("музыка") == [song]
    for result in (catalog.find_by_name(""), catalog.find_by_category("фильм")):
        result.clear()
    assert list(catalog) == [movie, song]
    assert catalog.find_by_name("несуществующее") == []


def test_iteration_order_and_readding() -> None:
    """Порядок повторяем; повторное добавление перемещает объект в конец."""
    first, second = make_item("b"), make_item("a")
    catalog = Catalog([first, second])
    assert list(catalog) == list(catalog) == [first, second]
    catalog.remove("b")
    catalog.add(first)
    assert list(catalog) == [second, first]


def test_non_media_is_rejected() -> None:
    """В каталог нельзя добавить произвольный объект."""
    with pytest.raises(InvalidMediaError):
        Catalog().add("not media")
