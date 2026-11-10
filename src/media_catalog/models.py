"""Описание одного элемента медиатеки."""

from dataclasses import dataclass

from media_catalog.errors import InvalidMediaError


@dataclass(frozen=True)
class Media:
    """Неизменяемый медиаобъект с проверяемыми полями."""

    id: str
    name: str
    category: str
    year: int
    creator: str
    minutes: int

    def __post_init__(self) -> None:
        """Проверяет поля при создании Media и вызывает InvalidMediaError при ошибке."""
        for field_name in ("id", "name", "category", "creator"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidMediaError(f"{field_name}: нужна непустая строка")
        for field_name in ("year", "minutes"):
            value = getattr(self, field_name)
            if type(value) is not int or value <= 0:
                raise InvalidMediaError(f"{field_name}: нужно целое число больше нуля")
