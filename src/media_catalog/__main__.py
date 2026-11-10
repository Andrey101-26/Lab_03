"""Терминальные команды медиатеки."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from media_catalog.catalog import Catalog
from media_catalog.errors import CatalogError
from media_catalog.models import Media
from media_catalog.storage import load_catalog, save_catalog


def create_parser() -> argparse.ArgumentParser:
    """Описать команды и аргументы терминала."""
    parser = argparse.ArgumentParser(description="Каталог медиаматериалов")
    parser.add_argument("--file", type=Path, default=Path("catalog.json"),
                        help="файл каталога (по умолчанию catalog.json)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="показать все материалы")
    commands.add_parser("count", help="показать число материалов")
    add = commands.add_parser("add", help="добавить материал")
    add.add_argument("id", help="уникальный строковый ID")
    add.add_argument("name", help="название")
    add.add_argument("category", help="вид материала")
    add.add_argument("year", type=int, help="год выпуска/создания")
    add.add_argument("creator", help="создатель")
    add.add_argument("minutes", type=int, help="длительность в минутах")
    for command, help_text in (("get", "найти по ID"), ("remove", "удалить по ID")):
        subparser = commands.add_parser(command, help=help_text)
        subparser.add_argument("id")
    find = commands.add_parser("find", help="поиск по названию или категории")
    group = find.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", help="часть названия без учёта регистра")
    group.add_argument("--category", help="точное название категории")
    save = commands.add_parser("save", help="сохранить копию каталога")
    save.add_argument("path", type=Path)
    load = commands.add_parser("load", help="заменить каталог данными из JSON")
    load.add_argument("path", type=Path)
    return parser


def show_item(item: Media) -> None:
    """Вывести все поля одного материала."""
    print(f"{item.id} | {item.name} | {item.category} | {item.year} | "
          f"{item.creator} | {item.minutes} мин.")


def main(argv: Sequence[str] | None = None) -> int:
    """Выполнить команду; вернуть 0 при успехе и 2 при ошибке."""
    args = create_parser().parse_args(argv)
    try:
        catalog = load_catalog(args.file) if args.file.exists() else Catalog()
        if args.command == "add":
            catalog.add(Media(args.id, args.name, args.category,
                              args.year, args.creator, args.minutes))
            save_catalog(catalog, args.file)
            print("Материал добавлен")
        elif args.command == "get":
            show_item(catalog.get(args.id))
        elif args.command == "remove":
            catalog.remove(args.id)
            save_catalog(catalog, args.file)
            print("Материал удалён")
        elif args.command == "count":
            print(len(catalog))
        elif args.command in ("list", "find"):
            if args.command == "list":
                items = list(catalog)
            elif args.name is not None:
                items = catalog.find_by_name(args.name)
            else:
                items = catalog.find_by_category(args.category)
            if not items:
                print("Материалы не найдены")
            for item in items:
                show_item(item)
        elif args.command == "save":
            save_catalog(catalog, args.path)
            print("Копия сохранена")
        elif args.command == "load":
            load_catalog(args.path, catalog)
            save_catalog(catalog, args.file)
            print("Каталог загружен")
    except CatalogError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
