"""Проверки команд терминала и сохранения между вызовами."""

import os
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Запустить реальную точку входа в отдельном процессе."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, "-m", "media_catalog", *args],
                          capture_output=True, text=True, encoding="utf-8", env=env)


def test_help() -> None:
    """Справка доступна без файла каталога."""
    result = run_cli("--help")
    assert result.returncode == 0
    assert "add" in result.stdout and "find" in result.stdout


def test_cli_lifecycle(tmp_path) -> None:
    """Команды сохраняют каталог и работают между независимыми запусками."""
    prefix = ("--file", str(tmp_path / "catalog.json"))
    assert run_cli(*prefix, "count").stdout.strip() == "0"
    added = run_cli(*prefix, "add", "001", "Солярис", "фильм", "1972", "Автор", "167")
    assert added.returncode == 0
    assert "Солярис" in run_cli(*prefix, "get", "001").stdout
    assert "Солярис" in run_cli(*prefix, "list").stdout
    assert "Солярис" in run_cli(*prefix, "find", "--name", "СОЛЯ").stdout
    assert "Солярис" in run_cli(*prefix, "find", "--category", "фильм").stdout
    duplicate = run_cli(*prefix, "add", "001", "Другой", "фильм", "2000", "Автор", "90")
    assert duplicate.returncode == 2 and "Ошибка" in duplicate.stderr
    backup = str(tmp_path / "backup.json")
    assert run_cli(*prefix, "save", backup).returncode == 0
    assert run_cli(*prefix, "remove", "001").returncode == 0
    assert run_cli(*prefix, "count").stdout.strip() == "0"
    assert run_cli(*prefix, "load", backup).returncode == 0
    assert run_cli(*prefix, "count").stdout.strip() == "1"
    assert run_cli(*prefix, "get", "missing").returncode == 2


def test_cli_bad_load_preserves_file(tmp_path) -> None:
    """Ошибка импорта не перезаписывает рабочий файл."""
    path = tmp_path / "catalog.json"
    prefix = ("--file", str(path))
    assert run_cli(*prefix, "add", "1", "Фильм", "фильм", "2000", "Автор", "90").returncode == 0
    original = path.read_bytes()
    broken = tmp_path / "bad.json"
    broken.write_text("{", encoding="utf-8")
    assert run_cli(*prefix, "load", str(broken)).returncode == 2
    assert path.read_bytes() == original


def test_cli_invalid_numbers(tmp_path) -> None:
    """Неверное число вызывает ошибку аргументов без создания файла."""
    path = tmp_path / "absent.json"
    result = run_cli("--file", str(path), "add", "1", "Film", "film", "bad", "Me", "90")
    assert result.returncode == 2
    assert not path.exists()
