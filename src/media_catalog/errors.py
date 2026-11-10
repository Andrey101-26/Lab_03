"""Предметные ошибки медиатеки."""


class CatalogError(Exception):
    """Базовая ошибка каталога."""


class InvalidMediaError(CatalogError):
    """Недопустимые данные медиаобъекта."""


class DuplicateIdError(CatalogError):
    """Идентификатор уже занят."""


class ItemNotFoundError(CatalogError):
    """Объект не найден."""


class UnsupportedVersionError(CatalogError):
    """Версия формата не поддерживается."""


class CorruptFileError(CatalogError):
    """Файл недоступен или содержит неверные данные."""
