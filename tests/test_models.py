"""Проверки инвариантов сущности."""

from dataclasses import FrozenInstanceError

import pytest

from media_catalog.errors import InvalidMediaError
from media_catalog.models import Media


def test_valid_media() -> None:
    """Допустимый объект сохраняет все поля."""
    item = Media("001", "Книга", "аудиокнига", 2020, "Автор", 90)
    assert (item.id, item.name, item.category, item.year, item.creator, item.minutes) == (
        "001", "Книга", "аудиокнига", 2020, "Автор", 90,
    )


@pytest.mark.parametrize("field,value", [
    ("id", "  "), ("id", 1), ("name", ""), ("name", " \t"), ("name", None),
    ("category", ""), ("creator", ""), ("year", 0), ("year", -1),
    ("year", True), ("year", "2020"), ("minutes", 0), ("minutes", -1),
    ("minutes", 1.5), ("minutes", False),
])
def test_invalid_media(field, value) -> None:
    """Неверные типы и значения отклоняются предметной ошибкой."""
    data = dict(id="1", name="Тест", category="фильм", year=2000, creator="Автор", minutes=90)
    data[field] = value
    with pytest.raises(InvalidMediaError):
        Media(**data)


def test_media_is_immutable() -> None:
    """Нельзя изменить ID или обойти проверки после создания."""
    item = Media("1", "Тест", "фильм", 2000, "Автор", 90)
    with pytest.raises(FrozenInstanceError):
        item.id = "2"
