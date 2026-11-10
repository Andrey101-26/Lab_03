# ЛР3. Медиатека

Каталог фильмов, музыки и аудиокниг. Python 3.10+.

## Установка

В терминале из корня проекта, с активным виртуальным окружением:

```powershell
python -m pip install -e .
python -m pip install pytest ruff mypy
```

Если окружение не активно, вместо `python` используйте `.\.venv\Scripts\python.exe`.

## Запуск

Точка входа: `src/media_catalog/__main__.py`.

```powershell
python -m media_catalog --help
python -m media_catalog add 001 "Солярис" "фильм" 1972 "Тарковский" 167
python -m media_catalog list
python -m media_catalog get 001
python -m media_catalog find --name "СОЛЯ"
python -m media_catalog find --category "фильм"
python -m media_catalog count
python -m media_catalog save backup.json
python -m media_catalog remove 001
python -m media_catalog load backup.json
```

Данные автоматически сохраняются в `catalog.json`. Другой файл:
`python -m media_catalog --file library.json list`.
`save` сохраняет копию, `load` заменяет текущий каталог.
Успех — код 0, ошибка — сообщение в stderr и код 2.

## Устройство

- `models.py` — dataclass Media и проверки полей.
- `catalog.py` — добавление, получение, удаление, поиск и протоколы.
- `storage.py` — JSON; `errors.py` — исключения; `constants.py` — версия формата.
- `tests/` — тесты модели, каталога, хранения и CLI.

Поля: id, name, category, year, creator, minutes. Строки непустые,
год и длительность — положительные целые числа. Объекты неизменяемые.
ID уникален и сравнивается точно. Поиск категории точный, названия — по подстроке
без учёта регистра. Поиск возвращает отдельный список.
Итерация — в порядке добавления; повторно добавленный объект попадает в конец.
Получение по ID — в среднем O(1), поиск по имени и категории — O(n).

JSON: `{"format_version": 1, "items": [...]}`. При неверных данных или неизвестной
версии загрузка отклоняется; существующий каталог остаётся без изменений.

## Проверки

```powershell
python -m pytest
python -m ruff check .
python -m mypy src/media_catalog
```
