"""Сохранение JSON и атомарная относительно каталога загрузка."""

import json
from dataclasses import asdict, fields
from pathlib import Path

from media_catalog.catalog import Catalog
from media_catalog.constants import FORMAT_VERSION
from media_catalog.errors import CatalogError, CorruptFileError, UnsupportedVersionError
from media_catalog.models import Media


def save_catalog(catalog: Catalog, path: str | Path) -> None:
    """Сохранить все поля и порядок объектов в UTF-8 JSON."""
    document = {"format_version": FORMAT_VERSION, "items": [asdict(item) for item in catalog]}
    try:
        Path(path).write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as error:
        raise CorruptFileError(f"Не удалось сохранить файл: {error}") from error


def load_catalog(path: str | Path, catalog: Catalog | None = None) -> Catalog:
    """Проверить весь документ и только затем заменить целевой каталог."""
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise CorruptFileError(f"Не удалось прочитать JSON: {error}") from error
    if not isinstance(document, dict) or "format_version" not in document:
        raise CorruptFileError("Нужен объект с format_version и items")
    version = document["format_version"]
    if type(version) is not int:
        raise CorruptFileError("format_version должен быть целым числом")
    if version != FORMAT_VERSION:
        raise UnsupportedVersionError(f"Версия {version} не поддерживается")
    if set(document) != {"format_version", "items"} or not isinstance(document["items"], list):
        raise CorruptFileError("Неверная структура документа")
    expected = {field.name for field in fields(Media)}
    candidate = Catalog()
    try:
        for record in document["items"]:
            if not isinstance(record, dict) or set(record) != expected:
                raise CorruptFileError("Неверный набор полей медиаобъекта")
            candidate.add(Media(**record))
    except (CatalogError, TypeError, ValueError) as error:
        raise CorruptFileError(f"Неверные данные объектов: {error}") from error
    if catalog is None:
        return candidate
    catalog.replace_all(candidate)
    return catalog
