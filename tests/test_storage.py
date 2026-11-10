"""Проверки JSON и отсутствия частичных изменений."""

import json
from dataclasses import asdict

import pytest

from media_catalog.catalog import Catalog
from media_catalog.errors import CorruptFileError, UnsupportedVersionError
from media_catalog.models import Media
from media_catalog.storage import load_catalog, save_catalog


def sample() -> Media:
    """Вернуть образец со всеми полями."""
    return Media("001", "Солярис", "фильм", 1972, "Андрей Тарковский", 167)


def test_round_trip(tmp_path) -> None:
    """Сохранение и загрузка сохраняют все поля и порядок."""
    items = [sample(), Media("2", "Соната", "музыка", 1801, "Бетховен", 15)]
    path = tmp_path / "catalog.json"
    save_catalog(Catalog(items), path)
    assert json.loads(path.read_text(encoding="utf-8"))["format_version"] == 1
    assert list(load_catalog(path)) == items


@pytest.mark.parametrize("contents", [
    "{", "[]", "{}", '{"format_version": true, "items": []}',
    '{"format_version": 1, "items": {}}',
    '{"format_version": 1, "items": [{}]}',
])
def test_corrupt_document(tmp_path, contents) -> None:
    """Неверный синтаксис и структура отклоняются."""
    path = tmp_path / "bad.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(CorruptFileError):
        load_catalog(path)


def test_unknown_version_keeps_catalog(tmp_path) -> None:
    """Неизвестная версия не меняет существующий каталог."""
    catalog = Catalog([sample()])
    path = tmp_path / "future.json"
    path.write_text('{"format_version": 99, "items": []}', encoding="utf-8")
    with pytest.raises(UnsupportedVersionError):
        load_catalog(path, catalog)
    assert list(catalog) == [sample()]


@pytest.mark.parametrize("failure", ["invalid", "duplicate", "missing_field"])
def test_failure_in_middle_is_atomic(tmp_path, failure) -> None:
    """Второй неверный объект не позволяет загрузить даже первый."""
    original = sample()
    catalog = Catalog([original])
    first = asdict(Media("new", "Новый", "фильм", 2020, "Автор", 80))
    bad = dict(first, id="bad")
    if failure == "invalid":
        bad["minutes"] = 0
    elif failure == "duplicate":
        bad["id"] = "new"
    else:
        del bad["creator"]
    path = tmp_path / "partial.json"
    path.write_text(json.dumps({"format_version": 1, "items": [first, bad]}), encoding="utf-8")
    with pytest.raises(CorruptFileError):
        load_catalog(path, catalog)
    assert list(catalog) == [original]
    assert catalog.get("001") is original
    assert "new" not in catalog


def test_success_replaces_and_empty_clears(tmp_path) -> None:
    """Успешная загрузка заменяет каталог, в том числе пустым."""
    catalog = Catalog([sample()])
    path = tmp_path / "empty.json"
    save_catalog(Catalog(), path)
    assert load_catalog(path, catalog) is catalog
    assert len(catalog) == 0


def test_missing_file(tmp_path) -> None:
    """Ошибка доступа преобразуется в предметное исключение."""
    with pytest.raises(CorruptFileError):
        load_catalog(tmp_path / "missing.json")
